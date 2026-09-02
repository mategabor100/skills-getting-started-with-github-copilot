from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


client = TestClient(app)
initial_activities = deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    activities.clear()
    activities.update(deepcopy(initial_activities))
    yield
    activities.clear()
    activities.update(deepcopy(initial_activities))


def test_get_activities_returns_activity_list():
    response = client.get("/activities")

    assert response.status_code == 200
    payload = response.json()
    assert "Chess Club" in payload
    assert payload["Chess Club"]["participants"] == [
        "michael@mergington.edu",
        "daniel@mergington.edu",
    ]


def test_signup_adds_participant():
    response = client.post(
        "/activities/Science%20Club/signup",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 200
    assert response.json() == {"message": "Signed up student@mergington.edu for Science Club"}
    assert "student@mergington.edu" in activities["Science Club"]["participants"]


def test_signup_rejects_duplicate_participant():
    client.post(
        "/activities/Science%20Club/signup",
        params={"email": "student@mergington.edu"},
    )

    response = client.post(
        "/activities/Science%20Club/signup",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Student already signed up for this activity"}


def test_signup_rejects_unknown_activity():
    response = client.post(
        "/activities/Unknown%20Club/signup",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_removes_participant():
    client.post(
        "/activities/Science%20Club/signup",
        params={"email": "student@mergington.edu"},
    )

    response = client.delete(
        "/activities/Science%20Club/signup",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 200
    assert response.json() == {"message": "Removed student@mergington.edu from Science Club"}
    assert "student@mergington.edu" not in activities["Science Club"]["participants"]


def test_unregister_rejects_non_participant():
    response = client.delete(
        "/activities/Science%20Club/signup",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Student is not signed up for this activity"}