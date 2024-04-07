from fastapi.testclient import TestClient
import pytest
from app.main import app
from app.config import settings
from app.database import get_db
from app.oauth2 import create_access_token
from pymongo import MongoClient

@pytest.fixture()
def client():
    def override_db():
        client = MongoClient(settings.mongo_url)
        db = client[settings.mongo_db_test]
        client.drop_database(settings.mongo_db_test)
        yield db

    app.dependency_overrides[get_db] = override_db

    yield TestClient(app)



# User Fixtures
@pytest.fixture
def test_user(client):
    user = {
        "email": "test@t.com",
        "first_name": "test",
        "last_name": "test",
        "username": "test",
        "password": "test"
    }

    response = client.post("/users", json=user)

    assert response.status_code == 201

    return user


@pytest.fixture
def user_token(test_user):
    return create_access_token({"username": test_user['username'], "email": test_user["email"]})


@pytest.fixture
def authorized_user(client, user_token):
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {user_token}"
    }

    return client