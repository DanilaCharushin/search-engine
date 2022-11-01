import pytest
from dramatiq import Broker, Worker

from app.apps.dramatiq import tasks


@pytest.mark.django_db(transaction=True)
def test_ping_task(broker: Broker, worker: Worker):
    task = tasks.ping_task.send(2)

    broker.join(tasks.ping_task.queue_name)
    worker.join()

    assert task.get_result() == "Done in 2 seconds"
