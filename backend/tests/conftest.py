import dramatiq
import pytest
from rest_framework.test import APIClient


@pytest.fixture()
def broker():
    broker = dramatiq.get_broker()
    broker.flush_all()
    return broker


@pytest.fixture()
def worker(broker: dramatiq.Broker):
    worker = dramatiq.Worker(broker, worker_timeout=100)
    worker.start()
    yield worker
    worker.stop()


@pytest.fixture()
def client() -> APIClient:
    return APIClient()
