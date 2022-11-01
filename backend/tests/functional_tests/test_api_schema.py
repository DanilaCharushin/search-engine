import pytest
from rest_framework.test import APIClient


@pytest.mark.django_db(transaction=True)
def test_api_schema(client: APIClient):
    response = client.get("/api/schema/")
    assert response.status_code == 200
