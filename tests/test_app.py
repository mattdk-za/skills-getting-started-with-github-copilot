import pytest
from fastapi.testclient import TestClient

import src.app as app_module



@pytest.fixture
def activities_data(monkeypatch):
    test_activities = {
        "Programming Class": {
            "description": "Learn programming fundamentals",
            "schedule": "Tuesdays",
            "max_participants": 3,
            "participants": ["student@example.com", "other@example.com"],
        }
    }
    monkeypatch.setattr(app_module, "activities", test_activities)
    return test_activities


@pytest.fixture
def client(activities_data):
    return TestClient(app_module.app)


def test_get_activities_returns_activity_data(client, activities_data):
    # Arrange
    expected_activities = activities_data

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == expected_activities


def test_signup_adds_participant(client, activities_data):
    # Arrange
    email = "newstudent@example.com"

    # Act
    response = client.post(
        f"/activities/Programming%20Class/signup?email={email}"
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": "Signed up newstudent@example.com for Programming Class"
    }
    assert activities_data["Programming Class"]["participants"] == [
        "student@example.com",
        "other@example.com",
        "newstudent@example.com",
    ]


def test_signup_returns_404_for_missing_activity(client, activities_data):
    # Arrange
    email = "newstudent@example.com"

    # Act
    response = client.post(f"/activities/Unknown%20Club/signup?email={email}")

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}
    assert activities_data["Programming Class"]["participants"] == [
        "student@example.com",
        "other@example.com",
    ]


def test_signup_returns_400_for_duplicate_participant(client, activities_data):
    # Arrange
    email = "student@example.com"

    # Act
    response = client.post(
        f"/activities/Programming%20Class/signup?email={email}"
    )

    # Assert
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Student already signed up for this activity"
    }
    assert activities_data["Programming Class"]["participants"] == [
        "student@example.com",
        "other@example.com",
    ]


def test_unregister_removes_participant_and_preserves_others(
    client, activities_data
):
    # Arrange
    email = "student@example.com"

    # Act
    response = client.delete(
        "/activities/Programming%20Class/unregister?email=student@example.com"
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": "Unregistered student@example.com from Programming Class"
    }
    assert activities_data["Programming Class"]["participants"] == [
        "other@example.com"
    ]


def test_unregister_returns_404_for_missing_activity(client, activities_data):
    # Arrange
    email = "student@example.com"

    # Act
    response = client.delete("/activities/Unknown%20Club/unregister?email=student@example.com")

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}
    assert activities_data["Programming Class"]["participants"] == [
        "student@example.com",
        "other@example.com",
    ]


def test_unregister_returns_400_for_unregistered_email(client, activities_data):
    # Arrange
    email = "missing@example.com"

    # Act
    response = client.delete(
        f"/activities/Programming%20Class/unregister?email={email}"
    )

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Student not registered for this activity"}
    assert activities_data["Programming Class"]["participants"] == [
        "student@example.com",
        "other@example.com",
    ]
