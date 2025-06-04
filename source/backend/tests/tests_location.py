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
TEST_LOCATION = {
    "building_name": "test 999",
    "lab_room_number": 900,
    "locker_number": 9
}
TEST_LOCATION_ID = None

@pytest.fixture(scope="module")
def client():
    """Create and configure a FastAPI test client"""
    with TestClient(app) as client:
        yield client

# Tests are defined in a specific order to ensure dependencies between tests are satisfied
# pytest will run tests in the order they appear in the file

def test_buildings(client):
    """Test the buildings endpoint to verify the list of buildings"""
    logger.info("Testing GET /backend/buildings endpoint")
    
    # Make the request
    response = client.get("/backend/buildings")
    
    # Assertions
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    data = response.json()
    assert "success" in data, "Response should contain 'success' field"
    assert data["success"] is True, "Success should be True"
    assert "buildings" in data, "Response should contain 'buildings' field"
    assert isinstance(data["buildings"], list), "Buildings should be a list"
    assert len(data["buildings"]) >= 3, "There should be at least 3 buildings"
    
    # Check required buildings are present
    assert "building 202" in data["buildings"], "Building '202' should be in the returned buildings"
    
    logger.info("Buildings test successful")

def test_lab_rooms_by_building(client):
    """Test the lab_rooms endpoint to verify the list of lab rooms for a specific building"""
    logger.info("Testing GET /backend/lab_rooms/building 202 endpoint")
    
    # Define the specific building to test
    building_name = "building 202"
    
    # Make the request
    response = client.get(f"/backend/lab_rooms/{building_name}")
    
    # Assertions
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    data = response.json()
    assert "success" in data, "Response should contain 'success' field"
    assert data["success"] is True, "Success should be True"
    assert "lab_rooms" in data, "Response should contain 'lab_rooms' field"
    assert isinstance(data["lab_rooms"], list), "Lab rooms should be a list"
    assert len(data["lab_rooms"]) >= 3, "There should be at least 3 lab rooms"
    
    assert 100 in data["lab_rooms"], f"Lab room '100' should be in the returned lab rooms for '{building_name}'"
    
    # Log the building name in the message to make it explicit
    logger.info(f"Lab rooms by building test successful for '{building_name}'")

def test_locations(client):
    """Test the locations endpoint to verify the list of locations"""
    logger.info("Testing GET /backend/locations endpoint")
    
    # Make the request
    response = client.get("/backend/locations")
    
    # Assertions
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    data = response.json()
    assert "success" in data, "Response should contain 'success' field"
    assert data["success"] is True, "Success should be True"
    assert "locations" in data, "Response should contain 'locations' field"
    assert isinstance(data["locations"], list), "Locations should be a list"
    assert len(data["locations"]) >= 12, "There should be at least 12 locations"
    
    # Check at least one location matches our criteria
    found_test_location = False
    for location in data["locations"]:
        if (location["building_name"] == "building 202" and
            location["lab_room_number"] == 120 and
            location["locker_number"] == 5):
            found_test_location = True
            break
    
    assert found_test_location, "Expected location not found in the locations list"
    
    logger.info("Locations test successful")

def test_create_location(client):
    """Test creating a new location"""
    logger.info("Testing POST /backend/createlocation endpoint")
    
    global TEST_LOCATION_ID
    
    # Make the request
    response = client.post(
        "/backend/createlocation",
        json={
            "building_name": TEST_LOCATION["building_name"],
            "lab_room_number": TEST_LOCATION["lab_room_number"],
            "locker_number": TEST_LOCATION["locker_number"]
        }
    )
    
    # Assertions
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    data = response.json()
    assert "success" in data, "Response should contain 'success' field"
    assert data["success"] is True, f"Location creation should succeed, got: {data.get('message', 'No message')}"
    assert "location_id" in data, "Response should contain 'location_id' field"
    
    # Store the location ID for later tests
    TEST_LOCATION_ID = data["location_id"]
    
    # Verify the new location appears in the locations list
    verify_response = client.get("/backend/locations")
    verify_data = verify_response.json()
    
    found_new_location = False
    for location in verify_data["locations"]:
        if (location["location_id"] == TEST_LOCATION_ID and
            location["building_name"] == TEST_LOCATION["building_name"] and
            location["lab_room_number"] == TEST_LOCATION["lab_room_number"] and
            location["locker_number"] == TEST_LOCATION["locker_number"]):
            found_new_location = True
            break
    
    assert found_new_location, "Newly created location not found in the locations list"
    
    logger.info(f"Create location test successful. Created location ID: {TEST_LOCATION_ID}")

def test_update_location(client):
    """Test updating an existing location"""
    logger.info("Testing POST /backend/updatelocation endpoint")
    
    global TEST_LOCATION
    
    # Update the location
    updated_location = {
        "building_name": TEST_LOCATION["building_name"],
        "lab_room_number": 909,  # Changed from 900 to 909
        "locker_number": 99,      # Changed from 9 to 99
        "location_id": TEST_LOCATION_ID
    }
    
    # Make the request
    response = client.post(
        "/backend/updatelocation",
        json=updated_location
    )
    
    # Assertions
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    data = response.json()
    assert "success" in data, "Response should contain 'success' field"
    assert data["success"] is True, f"Location update should succeed, got: {data.get('message', 'No message')}"
    
    # Update test location for future tests
    TEST_LOCATION["lab_room_number"] = 909
    TEST_LOCATION["locker_number"] = 99
    
    # Verify the updated location appears in the locations list
    verify_response = client.get("/backend/locations")
    verify_data = verify_response.json()
    
    found_updated_location = False
    for location in verify_data["locations"]:
        if (location["location_id"] == TEST_LOCATION_ID and
            location["building_name"] == TEST_LOCATION["building_name"] and
            location["lab_room_number"] == TEST_LOCATION["lab_room_number"] and
            location["locker_number"] == TEST_LOCATION["locker_number"]):
            found_updated_location = True
            break
    
    assert found_updated_location, "Updated location not found in the locations list"
    
    logger.info("Update location test successful")

def test_check_location_with_inventory(client):
    """Test checking for inventory at an existing location known to have inventory"""
    logger.info("Testing GET /backend/checklocation endpoint - location with inventory")
    
    # Find a location with known inventory - building 202, lab room 100, locker 1
    locations_response = client.get("/backend/locations")
    locations_data = locations_response.json()
    
    location_with_inventory_id = None
    for location in locations_data["locations"]:
        if (location["building_name"] == "building 202" and
            location["lab_room_number"] == 100 and
            location["locker_number"] == 1):
            location_with_inventory_id = location["location_id"]
            break
    
    # Only proceed if we found the location
    if location_with_inventory_id:
        # Make the request
        response = client.get(f"/backend/checklocation/{location_with_inventory_id}")
        
        # Assertions
        assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
        
        data = response.json()
        assert "success" in data, "Response should contain 'success' field"
        assert data["success"] is True, "Success should be True"
        assert "has_inventory" in data, "Response should contain 'has_inventory' field"
        assert data["has_inventory"] is True, "Location should have inventory"
    else:
        # Log a warning if we couldn't find the test location
        logger.warning("Could not find test location with inventory. Skipping inventory check test.")
    
    logger.info("Check location with inventory test successful")

def test_check_location_without_inventory(client):
    """Test checking for inventory at a location known to have no inventory"""
    logger.info("Testing GET /backend/checklocation endpoint - location without inventory")
    
    # Make the request using our test location which should not have inventory
    response = client.get(f"/backend/checklocation/{TEST_LOCATION_ID}")
    
    # Assertions
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    data = response.json()
    assert "success" in data, "Response should contain 'success' field"
    assert data["success"] is True, "Success should be True"
    assert "has_inventory" in data, "Response should contain 'has_inventory' field"
    assert data["has_inventory"] is False, "Test location should not have inventory"
    
    logger.info("Check location without inventory test successful")

def test_delete_location(client):
    """Test deleting a location"""
    logger.info("Testing DELETE /backend/deletelocation endpoint")
    
    # Make the request
    response = client.delete(f"/backend/deletelocation/{TEST_LOCATION_ID}")
    
    # Assertions
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    data = response.json()
    assert "success" in data, "Response should contain 'success' field"
    assert data["success"] is True, f"Location deletion should succeed, got: {data.get('message', 'No message')}"
    
    # Verify the location no longer appears in the locations list
    verify_response = client.get("/backend/locations")
    verify_data = verify_response.json()
    
    for location in verify_data["locations"]:
        assert location["location_id"] != TEST_LOCATION_ID, "Deleted location should not be in the locations list"
    
    logger.info("Delete location test successful")

if __name__ == "__main__":
    # This allows running the tests directly with python instead of pytest
    pytest.main(["-v", __file__])
