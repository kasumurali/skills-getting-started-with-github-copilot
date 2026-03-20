import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


class TestActivities:
    """Test GET /activities endpoint"""
    
    def test_get_activities(self):
        """Test fetching all activities"""
        # Arrange
        expected_activities = ["Chess Club", "Programming Class", "Gym Class"]
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        assert response.status_code == 200
        assert isinstance(activities, dict)
        for activity in expected_activities:
            assert activity in activities
    
    def test_get_activities_structure(self):
        """Test each activity has correct data structure"""
        # Arrange
        required_fields = {"description", "schedule", "max_participants", "participants"}
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        assert response.status_code == 200
        for name, details in activities.items():
            assert all(field in details for field in required_fields)
            assert isinstance(details["participants"], list)
            assert isinstance(details["max_participants"], int)


class TestSignup:
    """Test POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_success(self):
        """Test successful student signup"""
        # Arrange
        email = "newstudent123@mergington.edu"
        activity = "Chess Club"
        
        # Act
        response = client.post(f"/activities/{activity}/signup?email={email}")
        result = response.json()
        
        # Assert
        assert response.status_code == 200
        assert "Signed up" in result["message"]
        assert email in result["message"]
    
    def test_signup_duplicate_prevents_double_registration(self):
        """Test that duplicate signup attempts are rejected"""
        # Arrange
        email = "duplicate@mergington.edu"
        activity = "Programming Class"
        
        # Act - First signup (success)
        first_response = client.post(f"/activities/{activity}/signup?email={email}")
        
        # Act - Duplicate signup (should fail)
        duplicate_response = client.post(f"/activities/{activity}/signup?email={email}")
        duplicate_result = duplicate_response.json()
        
        # Assert
        assert first_response.status_code == 200
        assert duplicate_response.status_code == 400
        assert "already signed up" in duplicate_result["detail"]
    
    def test_signup_nonexistent_activity_returns_404(self):
        """Test signup for non-existent activity returns 404"""
        # Arrange
        email = "test@mergington.edu"
        invalid_activity = "Nonexistent Club"
        
        # Act
        response = client.post(f"/activities/{invalid_activity}/signup?email={email}")
        result = response.json()
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in result["detail"]


class TestUnregister:
    """Test DELETE /activities/{activity_name}/signup endpoint"""
    
    def test_unregister_removes_participant(self):
        """Test successful participant unregistration"""
        # Arrange
        email = "unregister_test@mergington.edu"
        activity = "Art Studio"
        
        # Act - Sign up first
        signup_response = client.post(f"/activities/{activity}/signup?email={email}")
        
        # Act - Unregister
        unregister_response = client.delete(f"/activities/{activity}/signup?email={email}")
        unregister_result = unregister_response.json()
        
        # Assert
        assert signup_response.status_code == 200
        assert unregister_response.status_code == 200
        assert "Unregistered" in unregister_result["message"]
        assert email in unregister_result["message"]
    
    def test_unregister_nonexistent_participant_returns_400(self):
        """Test unregister from activity when student not signed up"""
        # Arrange
        email = "never_signed_up@mergington.edu"
        activity = "Drama Club"
        
        # Act
        response = client.delete(f"/activities/{activity}/signup?email={email}")
        result = response.json()
        
        # Assert
        assert response.status_code == 400
        assert "not signed up" in result["detail"]
    
    def test_unregister_nonexistent_activity_returns_404(self):
        """Test unregister from non-existent activity returns 404"""
        # Arrange
        email = "test@mergington.edu"
        invalid_activity = "Nonexistent Club"
        
        # Act
        response = client.delete(f"/activities/{invalid_activity}/signup?email={email}")
        result = response.json()
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in result["detail"]


class TestRoot:
    """Test root endpoint"""
    
    def test_root_redirects_to_static_index(self):
        """Test root endpoint redirects to static HTML file"""
        # Arrange
        expected_redirect_path = "/static/index.html"
        
        # Act
        response = client.get("/", follow_redirects=False)
        
        # Assert
        assert response.status_code == 307
        assert expected_redirect_path in response.headers["location"]
