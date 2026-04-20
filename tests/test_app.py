"""
Test suite for Mergington High School Management System API

Uses the AAA (Arrange-Act-Assert) testing pattern:
- Arrange: Set up test data and preconditions
- Act: Execute the code being tested
- Assert: Verify the results
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a TestClient instance for testing"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to their initial state after each test"""
    yield
    # Reset to initial state
    activities.clear()
    activities.update({
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Practice and compete in basketball games",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": []
        },
        "Soccer Club": {
            "description": "Train and play soccer matches",
            "schedule": "Wednesdays and Fridays, 3:00 PM - 4:30 PM",
            "max_participants": 22,
            "participants": []
        },
        "Art Club": {
            "description": "Explore various art forms and create projects",
            "schedule": "Mondays, 3:30 PM - 5:00 PM",
            "max_participants": 10,
            "participants": []
        },
        "Drama Club": {
            "description": "Act in plays and improve theatrical skills",
            "schedule": "Tuesdays, 4:00 PM - 5:30 PM",
            "max_participants": 12,
            "participants": []
        },
        "Debate Club": {
            "description": "Learn argumentation and debate techniques",
            "schedule": "Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 16,
            "participants": []
        },
        "Science Club": {
            "description": "Conduct experiments and learn about science",
            "schedule": "Fridays, 2:00 PM - 3:30 PM",
            "max_participants": 18,
            "participants": []
        }
    })


class TestRootEndpoint:
    """Tests for GET / endpoint"""

    def test_root_redirect_to_static(self, client):
        """Test that root endpoint redirects to /static/index.html"""
        # Arrange
        expected_status = 307
        expected_location = "/static/index.html"

        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == expected_status
        assert response.headers["location"] == expected_location


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_all_activities(self, client, reset_activities):
        """Test retrieving all activities"""
        # Arrange
        expected_status = 200
        expected_count = 9

        # Act
        response = client.get("/activities")
        data = response.json()

        # Assert
        assert response.status_code == expected_status
        assert isinstance(data, dict)
        assert len(data) == expected_count

    def test_get_activities_returns_correct_structure(self, client, reset_activities):
        """Test that activities have the correct structure"""
        # Arrange
        expected_keys = ["description", "schedule", "max_participants", "participants"]

        # Act
        response = client.get("/activities")
        data = response.json()
        chess_club = data["Chess Club"]

        # Assert
        for key in expected_keys:
            assert key in chess_club
        assert isinstance(chess_club["participants"], list)

    def test_get_activities_includes_all_activities(self, client, reset_activities):
        """Test that all activities are returned"""
        # Arrange
        expected_activities = [
            "Chess Club", "Programming Class", "Gym Class",
            "Basketball Team", "Soccer Club", "Art Club",
            "Drama Club", "Debate Club", "Science Club"
        ]

        # Act
        response = client.get("/activities")
        data = response.json()

        # Assert
        for activity in expected_activities:
            assert activity in data


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_new_student(self, client, reset_activities):
        """Test signing up a new student for an activity"""
        # Arrange
        activity_name = "Basketball Team"
        email = "alex@mergington.edu"
        expected_status = 200

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == expected_status
        assert "Signed up" in response.json()["message"]
        assert email in activities[activity_name]["participants"]

    def test_signup_multiple_students_same_activity(self, client, reset_activities):
        """Test multiple students signing up for the same activity"""
        # Arrange
        activity_name = "Soccer Club"
        email1 = "student1@mergington.edu"
        email2 = "student2@mergington.edu"
        expected_status = 200

        # Act
        response1 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email1}
        )
        response2 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email2}
        )

        # Assert
        assert response1.status_code == expected_status
        assert response2.status_code == expected_status
        assert email1 in activities[activity_name]["participants"]
        assert email2 in activities[activity_name]["participants"]

    def test_signup_student_already_enrolled(self, client, reset_activities):
        """Test that duplicate signup returns error"""
        # Arrange
        activity_name = "Art Club"
        email = "bob@mergington.edu"
        expected_error_status = 400
        expected_error_message = "already signed up"

        # Act - First signup
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Act - Second signup (duplicate)
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == expected_error_status
        assert expected_error_message in response.json()["detail"]

    def test_signup_to_nonexistent_activity(self, client, reset_activities):
        """Test signing up for an activity that doesn't exist"""
        # Arrange
        activity_name = "Nonexistent Club"
        email = "test@mergington.edu"
        expected_status = 404
        expected_error_message = "Activity not found"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == expected_status
        assert expected_error_message in response.json()["detail"]

    def test_signup_already_enrolled_student(self, client, reset_activities):
        """Test that students already in an activity cannot sign up again"""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already enrolled
        expected_status = 400
        expected_error_message = "already signed up"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == expected_status
        assert expected_error_message in response.json()["detail"]

    def test_signup_various_email_formats(self, client, reset_activities):
        """Test signups with various email formats"""
        # Arrange
        activity_name = "Drama Club"
        test_emails = [
            "john.doe@mergington.edu",
            "jane_smith@mergington.edu",
            "student123@mergington.edu"
        ]
        expected_status = 200

        # Act & Assert
        for email in test_emails:
            response = client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )
            assert response.status_code == expected_status

    def test_signup_response_format(self, client, reset_activities):
        """Test that signup response has correct format"""
        # Arrange
        activity_name = "Debate Club"
        email = "debater@mergington.edu"
        expected_status = 200

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        data = response.json()

        # Assert
        assert response.status_code == expected_status
        assert "message" in data
        assert isinstance(data["message"], str)


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""

    def test_unregister_existing_student(self, client, reset_activities):
        """Test unregistering an enrolled student"""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        expected_status = 200

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == expected_status
        assert "Unregistered" in response.json()["message"]
        assert email not in activities[activity_name]["participants"]

    def test_unregister_multiple_students(self, client, reset_activities):
        """Test unregistering multiple students from same activity"""
        # Arrange
        activity_name = "Programming Class"
        email1 = "emma@mergington.edu"
        email2 = "sophia@mergington.edu"
        expected_status = 200

        # Act
        response1 = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email1}
        )
        response2 = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email2}
        )

        # Assert
        assert response1.status_code == expected_status
        assert response2.status_code == expected_status
        assert email1 not in activities[activity_name]["participants"]
        assert email2 not in activities[activity_name]["participants"]

    def test_unregister_not_enrolled_student(self, client, reset_activities):
        """Test unregistering a student who isn't enrolled"""
        # Arrange
        activity_name = "Basketball Team"
        email = "notenrolled@mergington.edu"
        expected_status = 400
        expected_error_message = "not signed up"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == expected_status
        assert expected_error_message in response.json()["detail"]

    def test_unregister_from_nonexistent_activity(self, client, reset_activities):
        """Test unregistering from an activity that doesn't exist"""
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"
        expected_status = 404
        expected_error_message = "Activity not found"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == expected_status
        assert expected_error_message in response.json()["detail"]

    def test_unregister_response_format(self, client, reset_activities):
        """Test that unregister response has correct format"""
        # Arrange
        activity_name = "Gym Class"
        email = "john@mergington.edu"
        expected_status = 200

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        data = response.json()

        # Assert
        assert response.status_code == expected_status
        assert "message" in data
        assert isinstance(data["message"], str)


class TestIntegrationScenarios:
    """Integration tests combining multiple operations"""

    def test_signup_then_unregister(self, client, reset_activities):
        """Test signing up then unregistering"""
        # Arrange
        activity_name = "Science Club"
        email = "test_student@mergington.edu"
        expected_signup_status = 200
        expected_unregister_status = 200

        # Act - Sign up
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert signup successful
        assert signup_response.status_code == expected_signup_status
        assert email in activities[activity_name]["participants"]

        # Act - Unregister
        unregister_response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert unregister successful
        assert unregister_response.status_code == expected_unregister_status
        assert email not in activities[activity_name]["participants"]

    def test_signup_unregister_resignup(self, client, reset_activities):
        """Test signing up, unregistering, and signing up again"""
        # Arrange
        activity_name = "Art Club"
        email = "student@mergington.edu"
        expected_status = 200

        # Act - First signup
        client.post(f"/activities/{activity_name}/signup", params={"email": email})

        # Assert student enrolled
        assert email in activities[activity_name]["participants"]

        # Act - Unregister
        client.delete(f"/activities/{activity_name}/unregister", params={"email": email})

        # Assert student unenrolled
        assert email not in activities[activity_name]["participants"]

        # Act - Re-signup
        response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

        # Assert re-signup successful
        assert response.status_code == expected_status
        assert email in activities[activity_name]["participants"]

    def test_signup_to_multiple_activities(self, client, reset_activities):
        """Test signing up to multiple activities"""
        # Arrange
        email = "multi_student@mergington.edu"
        activities_to_join = ["Basketball Team", "Soccer Club", "Drama Club"]
        expected_status = 200

        # Act - Sign up for multiple activities
        for activity in activities_to_join:
            response = client.post(
                f"/activities/{activity}/signup",
                params={"email": email}
            )
            assert response.status_code == expected_status

        # Assert student is enrolled in all activities
        for activity in activities_to_join:
            assert email in activities[activity]["participants"]

    def test_activity_not_affected_by_other_operations(self, client, reset_activities):
        """Test that operations on one activity don't affect others"""
        # Arrange
        email = "student@mergington.edu"
        activity_1 = "Debate Club"
        activity_2 = "Chess Club"

        # Act - Sign up for two activities
        client.post(f"/activities/{activity_1}/signup", params={"email": email})
        client.post(f"/activities/{activity_2}/signup", params={"email": email})

        # Act - Unregister from first activity
        client.delete(f"/activities/{activity_1}/unregister", params={"email": email})

        # Assert only first activity is affected
        assert email not in activities[activity_1]["participants"]
        assert email in activities[activity_2]["participants"]


class TestEdgeCases:
    """Tests for edge cases and boundary conditions"""

    def test_activity_name_case_sensitive(self, client, reset_activities):
        """Test that activity names are case-sensitive"""
        # Arrange
        activity_name = "chess club"  # lowercase instead of "Chess Club"
        email = "test@mergington.edu"
        expected_status = 404

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == expected_status

    def test_empty_email_signup(self, client, reset_activities):
        """Test signup with empty email"""
        # Arrange
        activity_name = "Basketball Team"
        email = ""
        expected_status = 200

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == expected_status

    def test_email_with_special_characters(self, client, reset_activities):
        """Test email with special characters"""
        # Arrange
        activity_name = "Soccer Club"
        email = "student+test@mergington.edu"
        expected_status = 200

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == expected_status
        assert email in activities[activity_name]["participants"]
