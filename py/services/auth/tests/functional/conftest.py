import pytest


@pytest.fixture(scope="session")
def access_token(client):
    response = client.post("/jwt/encode/", json={"iss": "test", "payload": {"user_id": 1}})
    return response.json["access_token"]
