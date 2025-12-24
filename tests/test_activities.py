import pytest
from fastapi.testclient import TestClient
from src import app


@pytest.fixture
def client():
    return TestClient(app.app)


def test_get_activities(client):
    r = client.get("/activities")
    assert r.status_code == 200
    data = r.json()
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]


def test_signup_and_list(client):
    email = "test_signup@example.com"
    # Ensure clean state
    if email in app.activities["Chess Club"]["participants"]:
        app.activities["Chess Club"]["participants"].remove(email)

    r = client.post(f"/activities/Chess%20Club/signup?email={email}")
    assert r.status_code == 200
    assert "Signed up" in r.json().get("message", "")

    r2 = client.get("/activities")
    assert email in r2.json()["Chess Club"]["participants"]

    # Cleanup
    if email in app.activities["Chess Club"]["participants"]:
        app.activities["Chess Club"]["participants"].remove(email)


def test_prevent_multiple_signups(client):
    email = "test_multi@example.com"
    # Cleanup start
    for act in app.activities.values():
        if email in act["participants"]:
            act["participants"].remove(email)

    # Sign up for Chess Club
    r1 = client.post(f"/activities/Chess%20Club/signup?email={email}")
    assert r1.status_code == 200

    # Attempt to sign up for Gym Class -> should fail with 400
    r2 = client.post(f"/activities/Gym%20Class/signup?email={email}")
    assert r2.status_code == 400

    # Cleanup
    if email in app.activities["Chess Club"]["participants"]:
        app.activities["Chess Club"]["participants"].remove(email)


def test_delete_participant(client):
    email = "test_delete@example.com"
    # Ensure participant exists
    if email not in app.activities["Chess Club"]["participants"]:
        app.activities["Chess Club"]["participants"].append(email)

    r = client.delete(f"/activities/Chess%20Club/participants?email={email}")
    assert r.status_code == 200
    assert "Unregistered" in r.json().get("message", "")

    r2 = client.get("/activities")
    assert email not in r2.json()["Chess Club"]["participants"]


def test_delete_not_found(client):
    email = "nonexistent@example.com"
    # Ensure not present
    if email in app.activities["Chess Club"]["participants"]:
        app.activities["Chess Club"]["participants"].remove(email)

    r = client.delete(f"/activities/Chess%20Club/participants?email={email}")
    assert r.status_code == 404
