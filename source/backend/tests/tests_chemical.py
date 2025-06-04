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
SAVED_QUANTITY = None

@pytest.fixture(scope="module")
def client():
    """Create and configure a FastAPI test client"""
    with TestClient(app) as client:
        yield client

# Tests are defined in a specific order to ensure dependencies between tests are satisfied

def test_chemical_search_starts_with_name(client):
    """Test chemical search with a partial name match starting with"""
    logger.info("Testing POST /backend/chemsearch with partial name 'Amm'")
    
    # Make the request
    response = client.post(
        "/backend/chemsearch",
        json={"name": "Amm"}
    )
    
    # Assertions
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    data = response.json()
    assert "success" in data, "Response should contain 'success' field"
    assert data["success"] is True, "Success should be True"
    assert "results" in data, "Response should contain 'results' field"
    assert isinstance(data["results"], list), "Results should be a list"
    assert len(data["results"]) >= 5, "There should be at least 5 chemicals matching 'Amm'"
    
    # Verify all results have "Amm" in their names
    for result in data["results"]:
        assert "Amm" in result["name"], f"Chemical name '{result['name']}' should contain 'Amm'"
    
    logger.info("Chemical search starts with name test successful")

def test_chemical_search_contains_name(client):
    """Test chemical search with a partial name match containing"""
    logger.info("Testing POST /backend/chemsearch with partial name 'acid'")
    
    # Make the request
    response = client.post(
        "/backend/chemsearch",
        json={"name": "acid"}
    )
    
    # Assertions
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    data = response.json()
    assert "success" in data, "Response should contain 'success' field"
    assert data["success"] is True, "Success should be True"
    assert "results" in data, "Response should contain 'results' field"
    assert isinstance(data["results"], list), "Results should be a list"
    assert len(data["results"]) >= 20, "There should be at least 20 chemicals containing 'acid'"
    
    # Check for specific acids
    target_acids = ["Acetic Acid", "Boric Acid", "Nitric Acid"]
    found_acids = [acid for acid in target_acids if any(result["name"].lower() == acid.lower() for result in data["results"])]
    
    assert len(found_acids) > 0, f"At least one of {target_acids} should be found in the results"
    for acid in found_acids:
        logger.info(f"Found expected acid: {acid}")
    
    logger.info("Chemical search contains name test successful")

def test_chemical_search_by_building(client):
    """Test chemical search by building name"""
    logger.info("Testing POST /backend/chemsearch by building")
    
    # Make the request
    response = client.post(
        "/backend/chemsearch",
        json={"building_name": "building 202"}
    )
    
    # Assertions
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    data = response.json()
    assert "success" in data, "Response should contain 'success' field"
    assert data["success"] is True, "Success should be True"
    assert "results" in data, "Response should contain 'results' field"
    assert isinstance(data["results"], list), "Results should be a list"
    assert len(data["results"]) >= 20, "There should be at least 20 chemicals in building 202"
    
    # Check all results are from the correct building
    for result in data["results"]:
        assert result["building_name"] == "building 202", f"All results should be from 'building 202', got '{result['building_name']}'"
    
    logger.info("Chemical search by building test successful")

def test_chemical_search_by_building_and_lab(client):
    """Test chemical search by building name and lab room"""
    logger.info("Testing POST /backend/chemsearch by building and lab room")
    
    # Make the request
    response = client.post(
        "/backend/chemsearch",
        json={
            "building_name": "building 202",
            "lab_room_number": 120
        }
    )
    
    # Assertions
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    data = response.json()
    assert "success" in data, "Response should contain 'success' field"
    assert data["success"] is True, "Success should be True"
    assert "results" in data, "Response should contain 'results' field"
    assert isinstance(data["results"], list), "Results should be a list"
    assert len(data["results"]) >= 20, "There should be at least 20 chemicals in building 202, lab room 120"
    
    # Check all results are from the correct building and lab room
    for result in data["results"]:
        assert result["building_name"] == "building 202", f"Building should be 'building 202', got '{result['building_name']}'"
        assert result["lab_room_number"] == 120, f"Lab room should be 120, got {result['lab_room_number']}"
    
    logger.info("Chemical search by building and lab test successful")

def test_chemical_search_by_building_lab_and_locker(client):
    """Test chemical search by building name, lab room, and locker"""
    logger.info("Testing POST /backend/chemsearch by building, lab room, and locker")
    
    # Make the request
    response = client.post(
        "/backend/chemsearch",
        json={
            "building_name": "building 202",
            "lab_room_number": 120,
            "locker_number": 2
        }
    )
    
    # Assertions
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    data = response.json()
    assert "success" in data, "Response should contain 'success' field"
    assert data["success"] is True, "Success should be True"
    assert "results" in data, "Response should contain 'results' field"
    assert isinstance(data["results"], list), "Results should be a list"
    assert len(data["results"]) >= 5, "There should be at least 5 chemicals in building 202, lab room 120, locker 2"
    
    # Check all results are from the correct building, lab room, and locker
    for result in data["results"]:
        assert result["building_name"] == "building 202", f"Building should be 'building 202', got '{result['building_name']}'"
        assert result["lab_room_number"] == 120, f"Lab room should be 120, got {result['lab_room_number']}"
        assert result["locker_number"] == 2, f"Locker should be 2, got {result['locker_number']}"
    
    logger.info("Chemical search by building, lab, and locker test successful")

def test_chemical_search_by_hazard(client):
    """Test chemical search by hazard classification"""
    logger.info("Testing POST /backend/chemsearch by hazard classification")
    
    # Make the request
    response = client.post(
        "/backend/chemsearch",
        json={"hazard_classification": "skin"}
    )
    
    # Assertions
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    data = response.json()
    assert "success" in data, "Response should contain 'success' field"
    assert data["success"] is True, "Success should be True"
    assert "results" in data, "Response should contain 'results' field"
    assert isinstance(data["results"], list), "Results should be a list"
    assert len(data["results"]) >= 30, "There should be at least 30 chemicals with 'skin' in hazard classification"
    
    # Check all results have the hazard classification
    for result in data["results"]:
        assert result["hazard_classification"] and "skin" in result["hazard_classification"].lower(), \
            f"Hazard classification should contain 'skin', got '{result['hazard_classification']}'"
    
    logger.info("Chemical search by hazard test successful")

def test_chemical_search_by_hazard_and_building(client):
    """Test chemical search by hazard classification and building"""
    logger.info("Testing POST /backend/chemsearch by hazard classification and building")
    
    # Make the request
    response = client.post(
        "/backend/chemsearch",
        json={
            "hazard_classification": "skin",
            "building_name": "building 404"
        }
    )
    
    # Assertions
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    data = response.json()
    assert "success" in data, "Response should contain 'success' field"
    assert data["success"] is True, "Success should be True"
    assert "results" in data, "Response should contain 'results' field"
    assert isinstance(data["results"], list), "Results should be a list"
    assert len(data["results"]) >= 10, "There should be at least 10 chemicals with 'skin' in hazard in building 404"
    
    # Check all results have the hazard classification and are from the correct building
    for result in data["results"]:
        assert result["hazard_classification"] and "skin" in result["hazard_classification"].lower(), \
            f"Hazard classification should contain 'skin', got '{result['hazard_classification']}'"
        assert result["building_name"] == "building 404", \
            f"Building should be 'building 404', got '{result['building_name']}'"
    
    logger.info("Chemical search by hazard and building test successful")

def test_reorder_notification(client):
    """Test the reorder notification endpoint"""
    logger.info("Testing GET /backend/reorder_notif endpoint")
    
    # Make the request
    response = client.get("/backend/reorder_notif")
    
    # Assertions
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    data = response.json()
    assert "success" in data, "Response should contain 'success' field"
    assert data["success"] is True, "Success should be True"
    assert "users" in data, "Response should contain 'users' field"
    assert isinstance(data["users"], list), "Users should be a list"
    
    # Verify there's at least one chemical in the results
    chemicals_found = sum(len(user["chemicals"]) for user in data["users"])
    assert chemicals_found > 0, "There should be at least one chemical in the reorder notification results"
    
    logger.info("Reorder notification test successful")

def test_chemical_by_inventory_id(client):
    """Test getting chemical by inventory ID"""
    logger.info("Testing GET /backend/chemical/165 endpoint")
    
    global SAVED_QUANTITY
    
    # Make the request
    response = client.get("/backend/chemical/165")
    
    # Assertions
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    data = response.json()
    assert "success" in data, "Response should contain 'success' field"
    assert data["success"] is True, "Success should be True"
    assert "chemical" in data, "Response should contain 'chemical' field"
    
    # Save the quantity for later tests
    SAVED_QUANTITY = data["chemical"]["quantity"]
    logger.info(f"Saved quantity: {SAVED_QUANTITY}")
    
    logger.info("Chemical by inventory ID test successful")

def test_update_inventory_add(client):
    """Test updating inventory by adding quantity"""
    logger.info("Testing POST /backend/update_inventory - add action")
    
    global SAVED_QUANTITY
    
    # Make the request
    response = client.post(
        "/backend/update_inventory",
        json={
            "inventory_id": 165,
            "quantity": 1.1,
            "action": "add"
        }
    )
    
    # Assertions
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    data = response.json()
    assert "success" in data, "Response should contain 'success' field"
    assert data["success"] is True, "Success should be True"
    assert "new_quantity" in data, "Response should contain 'new_quantity' field"
    
    # Verify the new quantity is the saved quantity plus 1.1
    expected_quantity = SAVED_QUANTITY + 1.1
    assert abs(data["new_quantity"] - expected_quantity) < 0.001, \
        f"New quantity should be {expected_quantity}, got {data['new_quantity']}"
    
    logger.info("Update inventory add test successful")

def test_update_inventory_remove(client):
    """Test updating inventory by removing quantity"""
    logger.info("Testing POST /backend/update_inventory - remove action")
    
    global SAVED_QUANTITY
    
    # Make the request
    response = client.post(
        "/backend/update_inventory",
        json={
            "inventory_id": 165,
            "quantity": 1.1,
            "action": "remove"
        }
    )
    
    # Assertions
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    data = response.json()
    assert "success" in data, "Response should contain 'success' field"
    assert data["success"] is True, "Success should be True"
    assert "new_quantity" in data, "Response should contain 'new_quantity' field"
    
    # Verify the new quantity is back to the original saved quantity
    assert abs(data["new_quantity"] - SAVED_QUANTITY) < 0.001, \
        f"New quantity should be back to original {SAVED_QUANTITY}, got {data['new_quantity']}"
    
    logger.info("Update inventory remove test successful")

if __name__ == "__main__":
    # This allows running the tests directly with python instead of pytest
    pytest.main(["-v", __file__])
