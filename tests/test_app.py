import pytest
from fastapi.testclient import TestClient
import copy
from src.app import app, activities

# Initial activities data for resetting
INITIAL_ACTIVITIES = copy.deepcopy(activities)

@pytest.fixture
def client():
    """Test client for FastAPI app."""
    return TestClient(app)

@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to initial state before each test."""
    global activities
    activities.clear()
    activities.update(copy.deepcopy(INITIAL_ACTIVITIES))

def test_get_activities(client):
    """Test GET /activities returns the activities data."""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]
    assert "description" in data["Chess Club"]
    assert "schedule" in data["Chess Club"]
    assert "max_participants" in data["Chess Club"]

def test_signup_success(client, reset_activities):
    """Test successful signup for an activity."""
    email = "newstudent@mergington.edu"
    activity_name = "Chess Club"
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 200
    result = response.json()
    assert "Signed up" in result["message"]
    assert email in result["message"]

    # Verify the participant was added
    response2 = client.get("/activities")
    data = response2.json()
    assert email in data[activity_name]["participants"]

def test_signup_activity_not_found(client, reset_activities):
    """Test signup for non-existent activity."""
    email = "student@mergington.edu"
    activity_name = "NonExistent Activity"
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 404
    result = response.json()
    assert result["detail"] == "Activity not found"

def test_signup_already_signed_up(client, reset_activities):
    """Test signup when student is already signed up."""
    email = "michael@mergington.edu"  # Already in Chess Club
    activity_name = "Chess Club"
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 400
    result = response.json()
    assert result["detail"] == "Student already signed up"

def test_unregister_success(client, reset_activities):
    """Test successful unregister from an activity."""
    email = "michael@mergington.edu"
    activity_name = "Chess Club"
    response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
    assert response.status_code == 200
    result = response.json()
    assert "Unregistered" in result["message"]
    assert email in result["message"]

    # Verify the participant was removed
    response2 = client.get("/activities")
    data = response2.json()
    assert email not in data[activity_name]["participants"]

def test_unregister_activity_not_found(client, reset_activities):
    """Test unregister from non-existent activity."""
    email = "student@mergington.edu"
    activity_name = "NonExistent Activity"
    response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
    assert response.status_code == 404
    result = response.json()
    assert result["detail"] == "Activity not found"

def test_unregister_not_signed_up(client, reset_activities):
    """Test unregister when student is not signed up."""
    email = "notsignedup@mergington.edu"
    activity_name = "Chess Club"
    response = client.delete(f"/activities/{activity_name}/unregister?email={email}")
    assert response.status_code == 400
    result = response.json()
    assert result["detail"] == "Student not signed up for this activity"