import logging
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

from dramatiq import Broker, Message, Middleware, Worker
from dramatiq.common import current_millis

logger = logging.getLogger(__name__)

DB_PATH = os.getenv("dramatiq_prom_db", "tmp/metrics")
SERVER_PORT = 9191

os.makedirs(DB_PATH, exist_ok=True)


class Prometheus(Middleware):
    def __init__(self):
        self.delayed_messages = set()
        self.message_start_times = {}

    @property
    def forks(self):
        return [_run_exposition_server]

    def after_process_boot(self, broker: Broker):
        os.environ["PROMETHEUS_MULTIPROC_DIR"] = DB_PATH
        os.environ["prometheus_multiproc_dir"] = DB_PATH

        import prometheus_client as prom

        logger.debug("Setting up metrics...")
        registry = prom.CollectorRegistry()
        self.total_messages = prom.Counter(
            "dramatiq_messages_total",
            "The total number of messages processed.",
            ["pid", "queue_name", "actor_name"],
            registry=registry,
        )
        self.total_errored_messages = prom.Counter(
            "dramatiq_message_errors_total",
            "The total number of errored messages.",
            ["pid", "queue_name", "actor_name"],
            registry=registry,
        )
        self.total_retried_messages = prom.Counter(
            "dramatiq_message_retries_total",
            "The total number of retried messages.",
            ["pid", "queue_name", "actor_name"],
            registry=registry,
        )
        self.total_rejected_messages = prom.Counter(
            "dramatiq_message_rejects_total",
            "The total number of dead-lettered messages.",
            ["pid", "queue_name", "actor_name"],
            registry=registry,
        )
        self.inprogress_messages = prom.Gauge(
            "dramatiq_messages_inprogress",
            "The number of messages in progress.",
            ["pid", "queue_name", "actor_name"],
            registry=registry,
            multiprocess_mode="livesum",
        )
        self.inprogress_delayed_messages = prom.Gauge(
            "dramatiq_delayed_messages_inprogress",
            "The number of delayed messages in memory.",
            ["queue_name", "actor_name"],
            registry=registry,
        )
        self.message_durations = prom.Histogram(
            "dramatiq_message_duration_milliseconds",
            "The time spent processing messages.",
            ["pid", "queue_name", "actor_name"],
            buckets=(
                5,
                10,
                25,
                50,
                75,
                100,
                250,
                500,
                750,
                1000,
                2500,
                5000,
                7500,
                10000,
                30000,
                60000,
                600000,
                900000,
                float("inf"),
            ),
            registry=registry,
        )
        self.threads_count = prom.Gauge(
            "dramatiq_threads_count",
            "The number of threads of each worker.",
            ["pid"],
            registry=registry,
        )
        self.workers_count = prom.Gauge(
            "dramatiq_workers_count",
            "The number of workers.",
            ["pid"],
            registry=registry,
        )

    def after_worker_boot(self, broker: Broker, worker: Worker):
        logger.debug("Worker starts!")
        labels = (os.getpid(),)
        self.threads_count.labels(*labels).inc(len(worker.workers))
        self.workers_count.labels(*labels).inc()

    def after_worker_shutdown(self, broker: Broker, worker: Worker):
        labels = (os.getpid(),)
        self.threads_count.labels(*labels).dec(len(worker.workers))
        self.workers_count.labels(*labels).dec()

        from prometheus_client import multiprocess

        logger.debug("Marking process dead...")
        multiprocess.mark_process_dead(os.getpid(), DB_PATH)

    def after_nack(self, broker: Broker, message: Message):
        labels = (os.getpid(), message.queue_name, message.actor_name)
        self.total_rejected_messages.labels(*labels).inc()

    def after_enqueue(self, broker: Broker, message: Message, delay):
        if "retries" in message.options:
            labels = (os.getpid(), message.queue_name, message.actor_name)
            self.total_retried_messages.labels(*labels).inc()

    def before_delay_message(self, broker: Broker, message: Message):
        labels = (message.queue_name, message.actor_name)
        self.delayed_messages.add(message.message_id)
        self.inprogress_delayed_messages.labels(*labels).inc()

    def before_process_message(self, broker: Broker, message: Message):
        if message.message_id in self.delayed_messages:
            labels = (message.queue_name, message.actor_name)
            self.delayed_messages.remove(message.message_id)
            self.inprogress_delayed_messages.labels(*labels).dec()

        labels = (os.getpid(), message.queue_name, message.actor_name)
        self.inprogress_messages.labels(*labels).inc()
        self.message_start_times[message.message_id] = current_millis()

    def after_process_message(self, broker: Broker, message: Message, *, result=None, exception=None):
        labels = (os.getpid(), message.queue_name, message.actor_name)
        message_start_time = self.message_start_times.pop(message.message_id, current_millis())
        message_duration = current_millis() - message_start_time
        self.message_durations.labels(*labels).observe(message_duration)
        self.inprogress_messages.labels(*labels).dec()
        self.total_messages.labels(*labels).inc()
        if exception is not None:
            self.total_errored_messages.labels(*labels).inc()

    after_skip_message = after_process_message


class MetricsHandler(BaseHTTPRequestHandler):
    def do_GET(self):  # noqa
        os.environ["PROMETHEUS_MULTIPROC_DIR"] = DB_PATH
        os.environ["prometheus_multiproc_dir"] = DB_PATH

        # These imports must happen at runtime.  See above.
        import prometheus_client as prom
        from prometheus_client import multiprocess as prom_mp

        registry = prom.CollectorRegistry()
        prom_mp.MultiProcessCollector(registry)
        output = prom.generate_latest(registry)
        self.send_response(200)
        self.send_header("content-type", prom.CONTENT_TYPE_LATEST)
        self.end_headers()
        self.wfile.write(output)

    def log_message(self, fmt, *args):
        logger.debug(fmt, *args)


def _run_exposition_server():
    logger.debug("Starting exposition server...")

    address = ("0.0.0.0", SERVER_PORT)
    httpd = HTTPServer(address, MetricsHandler)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.debug("Stopping exposition server...")
        httpd.shutdown()

    return 0
