import os
import sys
import pytest
import logging
from fastapi.testclient import TestClient

# Set environment variables for testing - still need these for app configuration
os.environ["LOCAL_DEV"] = "true" 
os.environ["API_KEY_SECURITY"] = "disabled"
os.environ["SECRET_KEY"] = "test_secret_key"

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import the FastAPI app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.main import app

# Global variables to store test data between tests
TEST_USER = {
    "username": "testuser",
    "password": "testuser",
    "email": "john.heaton@covestro.com",
    "role": "technician"
}

@pytest.fixture(scope="module")
def client():
    """Create and configure a FastAPI test client"""
    with TestClient(app) as client:
        yield client

# Tests are defined in a specific order to ensure dependencies between tests are satisfied
# pytest will run tests in the order they appear in the file

def test_user_roles(client):
    """Test the roles endpoint to verify the available user roles"""
    logger.info("Testing GET /backend/roles endpoint")
    
    # Make the request
    response = client.get("/backend/roles")
    
    # Assertions
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    data = response.json()
    assert "roles" in data, "Response should contain 'roles' field"
    assert isinstance(data["roles"], list), "Roles should be a list"
    
    # Check required roles are present
    required_roles = ["administrator", "inventory-taker", "manager", "technician"]
    for role in required_roles:
        assert role in data["roles"], f"Role '{role}' should be in the returned roles"
    
    logger.info("User roles test successful")

def test_get_users(client):
    """Test the users endpoint to verify users can be retrieved"""
    logger.info("Testing GET /backend/users endpoint")
    
    # Make the request
    response = client.get("/backend/users")
    
    # Assertions
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    data = response.json()
    assert "users" in data, "Response should contain 'users' field"
    assert isinstance(data["users"], list), "Users should be a list"
    assert len(data["users"]) >= 3, "There should be at least 3 users"
    
    # Extract usernames for easier checking
    usernames = [user["username"] for user in data["users"]]
    
    # Check required users are present
    required_users = ["john", "oscar", "bob"]
    for username in required_users:
        assert username in usernames, f"User '{username}' should be in the returned users"
    
    # Check fields
    for user in data["users"]:
        assert "username" in user, "Each user should have a username"
        assert "email" in user, "Each user should have an email_address"
        assert "role" in user, "Each user should have a role_name"
    
    logger.info("Get users test successful")

def test_create_user(client):
    """Test creating a new user"""
    logger.info("Testing POST /backend/createuser endpoint")
    
    # Make the request
    response = client.post(
        "/backend/createuser",
        json={
            "username": TEST_USER["username"],
            "password": TEST_USER["password"],
            "email": TEST_USER["email"],
            "role": TEST_USER["role"]
        }
    )
    
    # Assertions
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    data = response.json()
    assert "success" in data, "Response should contain 'success' field"
    assert data["success"] is True, f"User creation should succeed, got: {data.get('message', 'No message')}"
    
    logger.info("Create user test successful")

def test_get_user_info(client):
    """Test getting information about a specific user"""
    logger.info("Testing POST /backend/get_user_info endpoint")
    
    # Make the request
    response = client.post(
        "/backend/get_user_info",
        json={"username": TEST_USER["username"]}
    )
    
    # Assertions
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    data = response.json()
    assert "success" in data, "Response should contain 'success' field"
    assert data["success"] is True, f"Getting user info should succeed, got: {data.get('message', 'No message')}"
    
    # Verify the user data matches what was created
    assert data["username"] == TEST_USER["username"], f"Expected username {TEST_USER['username']}, got {data['username']}"
    assert data["email"] == TEST_USER["email"], f"Expected email {TEST_USER['email']}, got {data['email']}"
    assert data["role"] == TEST_USER["role"], f"Expected role {TEST_USER['role']}, got {data['role']}"
    
    logger.info("Get user info test successful")

def test_update_user(client):
    """Test updating a user's information"""
    logger.info("Testing POST /backend/updateuser endpoint")
    
    # Update the role to manager
    updated_user = {
        "username": TEST_USER["username"],
        "password": TEST_USER["password"],
        "email": TEST_USER["email"],
        "role": "manager"  # Changed from technician to manager
    }
    
    # Make the update request
    response = client.post(
        "/backend/updateuser",
        json=updated_user
    )
    
    # Assertions for update
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    data = response.json()
    assert "success" in data, "Response should contain 'success' field"
    assert data["success"] is True, f"User update should succeed, got: {data.get('message', 'No message')}"
    
    # Verify the update by getting the user info again
    verify_response = client.post(
        "/backend/get_user_info",
        json={"username": TEST_USER["username"]}
    )
    
    # Assertions for verification
    assert verify_response.status_code == 200, f"Expected status code 200, got {verify_response.status_code}"
    
    verify_data = verify_response.json()
    assert verify_data["success"] is True, "Getting user info after update should succeed"
    assert verify_data["role"] == "manager", f"Expected updated role 'manager', got {verify_data['role']}"
    
    logger.info("Update user test successful")

def test_delete_user_preferences(client):
    """Test deleting a user's preferences"""
    logger.info("Testing POST /backend/delete_user_preference endpoint")
    
    # Make the delete preferences request
    response = client.post(
        "/backend/delete_user_preference",
        json={"username": TEST_USER["username"]}
    )
    
    # Assertions
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    data = response.json()
    assert "success" in data, "Response should contain 'success' field"
    assert data["success"] is True, f"Preference deletion should succeed, got: {data.get('message', 'No message')}"
    
    logger.info("Delete user preferences test successful")

def test_update_user_preference_initial(client):
    """Test updating a user preference - initial value"""
    logger.info("Testing POST /backend/update_user_preference endpoint - initial value")
    
    # Make the update preference request
    response = client.post(
        "/backend/update_user_preference",
        json={
            "username": TEST_USER["username"],
            "key": "building",
            "value": "building 202"
        }
    )
    
    # Assertions
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    data = response.json()
    assert "success" in data, "Response should contain 'success' field"
    assert data["success"] is True, f"Preference update should succeed, got: {data.get('message', 'No message')}"
    
    logger.info("Update user preference (initial) test successful")

def test_update_user_preference_modified(client):
    """Test updating a user preference - modified value"""
    logger.info("Testing POST /backend/update_user_preference endpoint - modified value")
    
    # Make the update preference request
    response = client.post(
        "/backend/update_user_preference",
        json={
            "username": TEST_USER["username"],
            "key": "building",
            "value": "building 319"
        }
    )
    
    # Assertions
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    data = response.json()
    assert "success" in data, "Response should contain 'success' field"
    assert data["success"] is True, f"Preference update should succeed, got: {data.get('message', 'No message')}"
    
    logger.info("Update user preference (modified) test successful")

def test_get_user_preferences(client):
    """Test getting user preferences"""
    logger.info("Testing POST /backend/get_user_preferences endpoint")
    
    # Make the get preferences request
    response = client.post(
        "/backend/get_user_preferences",
        json={"username": TEST_USER["username"]}
    )
    
    # Assertions
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    data = response.json()
    assert "success" in data, "Response should contain 'success' field"
    assert data["success"] is True, f"Getting preferences should succeed, got: {data.get('message', 'No message')}"
    assert "preferences" in data, "Response should contain 'preferences' field"
    
    # Verify the preference value
    preferences = data["preferences"]
    assert "building" in preferences, "Preference 'building' should be in the preferences"
    assert preferences["building"] == "building 319", f"Expected 'building' value to be 'building 319', got {preferences.get('building')}"
    
    logger.info("Get user preferences test successful")

def test_delete_user_preferences_again(client):
    """Test deleting a user's preferences again"""
    logger.info("Testing POST /backend/delete_user_preference endpoint (again)")
    
    # Make the delete preferences request
    response = client.post(
        "/backend/delete_user_preference",
        json={"username": TEST_USER["username"]}
    )
    
    # Assertions
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    data = response.json()
    assert "success" in data, "Response should contain 'success' field"
    assert data["success"] is True, f"Preference deletion should succeed, got: {data.get('message', 'No message')}"
    
    logger.info("Delete user preferences (again) test successful")

def test_user_login(client):
    """Test user login functionality"""
    logger.info("Testing POST /backend/login endpoint")
    
    # Make the login request
    response = client.post(
        "/backend/login",
        json={
            "username": TEST_USER["username"],
            "password": TEST_USER["password"]
        }
    )
    
    # Assertions
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    data = response.json()
    assert "success" in data, "Response should contain 'success' field"
    assert data["success"] is True, f"Login should succeed, got: {data.get('message', 'No message')}"
    assert "role" in data, "Response should contain 'role' field"
    assert data["role"] == "manager", f"Role should be 'manager', got {data.get('role')}"
    
    logger.info("User login test successful")

def test_update_password(client):
    """Test updating user password"""
    logger.info("Testing POST /backend/updatepassword endpoint")
    
    # Update the password
    response = client.post(
        "/backend/updatepassword",
        json={
            "username": TEST_USER["username"],
            "old_password": TEST_USER["password"],
            "new_password": "fred"
        }
    )
    
    # Assertions for password update
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    data = response.json()
    assert "success" in data, "Response should contain 'success' field"
    assert data["success"] is True, f"Password update should succeed, got: {data.get('message', 'No message')}"
    
    # Update our test user record to reflect the password change
    TEST_USER["password"] = "fred"
    
    # Verify login with the new password
    login_response = client.post(
        "/backend/login",
        json={
            "username": TEST_USER["username"],
            "password": TEST_USER["password"]
        }
    )
    
    # Assertions for login verification
    assert login_response.status_code == 200, f"Expected status code 200, got {login_response.status_code}"
    
    login_data = login_response.json()
    assert login_data["success"] is True, f"Login with new password should succeed, got: {login_data.get('message', 'No message')}"
    
    logger.info("Update password test successful")

def test_delete_user(client):
    """Test deleting a user"""
    logger.info("Testing POST /backend/deleteuser endpoint")
    
    # Make the delete request
    response = client.post(
        "/backend/deleteuser",
        json={"username": TEST_USER["username"]}
    )
    
    # Assertions for delete
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    data = response.json()
    assert "success" in data, "Response should contain 'success' field"
    assert data["success"] is True, f"User deletion should succeed, got: {data.get('message', 'No message')}"
    
    # Verify the deletion by trying to get the user info
    verify_response = client.post(
        "/backend/get_user_info",
        json={"username": TEST_USER["username"]}
    )
    
    # The user should no longer exist
    verify_data = verify_response.json()
    assert verify_data["success"] is False, "User should no longer exist after deletion"
    assert "not found" in verify_data.get("message", "").lower(), "Error message should indicate user not found"
    
    logger.info("Delete user test successful")

if __name__ == "__main__":
    # This allows running the tests directly with python instead of pytest
    pytest.main(["-v", __file__])
