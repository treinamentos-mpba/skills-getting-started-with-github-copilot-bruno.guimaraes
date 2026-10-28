from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src import app as app_module


@pytest.fixture
def client(monkeypatch):
    activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu"],
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu"],
        },
    }
    monkeypatch.setattr(app_module, "activities", activities)
    return TestClient(app_module.app), activities


def test_root_redirects_to_static_index(client):
    # Arrange
    test_client, _ = client

    # Act
    response = test_client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_available_activities(client):
    # Arrange
    test_client, activities = client
    expected_activities = deepcopy(activities)

    # Act
    response = test_client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == expected_activities


def test_signup_adds_student_to_activity(client):
    # Arrange
    test_client, activities = client
    email = "student@mergington.edu"

    # Act
    response = test_client.post(
        "/activities/Chess Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}
    assert email in activities["Chess Club"]["participants"]


def test_signup_returns_not_found_for_unknown_activity(client):
    # Arrange
    test_client, _ = client

    # Act
    response = test_client.post(
        "/activities/Unknown Club/signup",
        params={"email": "student@mergington.edu"},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_signup_returns_bad_request_for_existing_participant(client):
    # Arrange
    test_client, _ = client

    # Act
    response = test_client.post(
        "/activities/Chess Club/signup",
        params={"email": "michael@mergington.edu"},
    )

    # Assert
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Student already signed up for this activity"
    }


def test_unregister_removes_student_from_activity(client):
    # Arrange
    test_client, activities = client
    email = "michael@mergington.edu"

    # Act
    response = test_client.delete(
        "/activities/Chess Club/participants",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Unregistered {email} from Chess Club"
    }
    assert email not in activities["Chess Club"]["participants"]


def test_unregister_returns_not_found_for_unknown_activity(client):
    # Arrange
    test_client, _ = client

    # Act
    response = test_client.delete(
        "/activities/Unknown Club/participants",
        params={"email": "student@mergington.edu"},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_returns_not_found_for_unregistered_student(client):
    # Arrange
    test_client, _ = client

    # Act
    response = test_client.delete(
        "/activities/Chess Club/participants",
        params={"email": "student@mergington.edu"},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Student is not signed up for this activity"
    }
