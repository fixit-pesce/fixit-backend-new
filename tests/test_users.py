import pytest

@pytest.fixture(scope = "module")
def sample_input_data_user():
    return {
        "username": "janedoe",
        "email": "janedoe@example.com",
        "first_name": "Jane",
        "last_name": "Doe",
        "password": "123"
    }


def test_create_user(client, sample_input_data_user):
    response = client.post("/users/", json = sample_input_data_user)
    assert response.status_code == 201


def test_create_user_duplicate(client, sample_input_data_user):
    response = client.post("/users/", json = sample_input_data_user)
    assert response.status_code == 201

    response = client.get("/users/janedoe")
    print(response.json())

    response = client.post("/users/", json = sample_input_data_user)
    assert response.status_code == 409


def test_get_user(client, authorized_user, sample_input_data_user):
    response = client.get("/users/test")
    assert response.status_code == 200