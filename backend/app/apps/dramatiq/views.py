import logging

from django.http import HttpRequest, HttpResponse

from .tasks import ping_task

logger = logging.getLogger(__name__)


def ping_view(request: HttpRequest) -> HttpResponse:
    time_to_sleep = float(request.GET.get("time", "0"))  # noqa
    delay = float(request.GET.get("delay", "0"))  # noqa
    batch_size = int(request.GET.get("batch", "1"))  # noqa

    logger.debug(f"{time_to_sleep=}")
    logger.debug(f"{delay=}")
    logger.debug(f"{batch_size=}")

    messages = []
    for i in range(batch_size):
        task = ping_task.send_with_options(args=(time_to_sleep,), delay=delay)
        message = f"{i + 1}. Ping task {repr(task)} sent with!"
        logger.debug(message)
        messages.append(message)

    message = "\n".join(messages)
    return HttpResponse(f"{batch_size} tasks sent!\n{message}")
