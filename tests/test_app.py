from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)


def reset_activities():
    for activity in activities.values():
        activity["participants"] = []
    activities["Programming Class"]["participants"] = ["student@example.com"]


def test_unregister_participant_removes_email_from_activity():
    reset_activities()

    response = client.delete(
        "/activities/Programming%20Class/unregister?email=student@example.com"
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": "Unregistered student@example.com from Programming Class"
    }
    assert activities["Programming Class"]["participants"] == []


def test_unregister_participant_returns_404_for_missing_activity():
    reset_activities()

    response = client.delete("/activities/Unknown%20Club/unregister?email=student@example.com")

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_participant_returns_400_for_missing_email():
    reset_activities()

    response = client.delete(
        "/activities/Programming%20Class/unregister?email=missing@example.com"
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Student not registered for this activity"}
