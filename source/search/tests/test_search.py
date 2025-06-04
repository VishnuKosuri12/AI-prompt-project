import os
import sys
import json
import pytest
from unittest.mock import patch, MagicMock, Mock
from flask import session, url_for

# Set necessary environment variables before importing search
os.environ['BASE_URL'] = 'http://localhost'
os.environ['SECRET_KEY'] = 'test_secret_key'

# Add the parent directory to sys.path to import search.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Import search after setting environment variables
import search

@pytest.fixture
def client():
    """Create and configure a Flask test client"""
    search.app.config.update({
        "TESTING": True,
        "SECRET_KEY": "test_secret_key"
    })
    
    with search.app.test_client() as client:
        # Establish application context
        with search.app.app_context():
            yield client

@pytest.fixture
def mock_session_user():
    """Mock an authenticated user session"""
    with patch('flask.session', {"user": "testuser", "role": "technician", 
                              "pref_building": "Building 101", 
                              "pref_lab_room": "Lab 202"}):
        yield

@pytest.fixture
def mock_requests_get():
    """Mock requests.get for shared components"""
    with patch('requests.get') as mock_get:
        # Setup mock response for header
        mock_header_response = Mock()
        mock_header_response.status_code = 200
        mock_header_response.text = "<header>Test Header</header>"
        
        # Setup mock response for navigation
        mock_nav_response = Mock()
        mock_nav_response.status_code = 200
        mock_nav_response.text = "<nav>Test Navigation</nav>"
        
        # Configure the mock to return different responses based on URL
        def mock_get_response(url, **kwargs):
            if "header" in url:
                return mock_header_response
            elif "navigation" in url:
                return mock_nav_response
            else:
                mock_default = Mock()
                mock_default.status_code = 404
                return mock_default
                
        mock_get.side_effect = mock_get_response
        yield mock_get

@pytest.fixture
def mock_api_client():
    """Mock the api_client module"""
    with patch('api_client.post') as mock_post, \
         patch('api_client.get') as mock_get:
        
        # Setup default responses
        mock_post_response = Mock()
        mock_post_response.status_code = 200
        mock_post_response.json.return_value = {"success": True}
        mock_post.return_value = mock_post_response
        
        mock_get_response = Mock()
        mock_get_response.status_code = 200
        mock_get_response.json.return_value = {"success": True}
        mock_get.return_value = mock_get_response
        
        yield {
            "post": mock_post,
            "get": mock_get
        }

@pytest.fixture
def mock_search_results():
    """Mock search results data"""
    return [
        {
            "id": 1,
            "name": "Acetone",
            "cas_number": "67-64-1",
            "chemical_formula": "C3H6O",
            "quantity": 2.5,
            "unit_of_measure": "L",
            "reorder_quantity": 1.0,
            "building_name": "Building 101",
            "lab_room_number": 202,
            "locker_number": 3,
            "signal_word": "Danger", 
            "physical_state": "Liquid"
        },
        {
            "id": 2,
            "name": "Ethanol",
            "cas_number": "64-17-5",
            "chemical_formula": "C2H5OH",
            "quantity": 5.0,
            "unit_of_measure": "L",
            "reorder_quantity": 2.0,
            "building_name": "Building 101",
            "lab_room_number": 202,
            "locker_number": 3,
            "signal_word": "Warning",
            "physical_state": "Liquid"
        }
    ]

@pytest.fixture
def mock_chemical_details():
    """Mock chemical details data"""
    return {
        "id": 1,
        "name": "Acetone",
        "cas_number": "67-64-1",
        "chemical_formula": "C3H6O",
        "quantity": 2.5,
        "unit_of_measure": "L",
        "reorder_quantity": 1.0,
        "building_name": "Building 101",
        "lab_room_number": 202,
        "locker_number": 3,
        "signal_word": "Danger",
        "physical_state": "Liquid",
        "hazard_statements": ["Highly flammable liquid and vapor", "Causes serious eye irritation"],
        "precautionary_statements": ["Keep away from heat/sparks/open flames/hot surfaces", "Wear protective gloves"],
        "pictograms": ["GHS02", "GHS07"]
    }

# Test Cases

def test_index_unauthenticated(client):
    """Test the search index route with unauthenticated user"""
    response = client.get('/search')
    # Should redirect to login
    assert response.status_code >= 300 and response.status_code < 400
    # Skip location check if it's not available
    if hasattr(response, 'location'):
        assert '/login' in response.location or 'login' in response.location

def test_search_authenticated_get(client, mock_session_user, mock_requests_get, mock_api_client):
    """Test the search route GET with authenticated user"""
    with client.session_transaction() as sess:
        sess['user'] = 'testuser'
        sess['role'] = 'technician'
        sess['pref_building'] = 'Building 101'
        sess['pref_lab_room'] = 'Lab 202'
    
    # Configure API responses for buildings and lab rooms
    buildings_response = MagicMock()
    buildings_response.status_code = 200
    buildings_response.json.return_value = {"success": True, "buildings": ["Building 101", "Building 102"]}
    
    lab_rooms_response = MagicMock()
    lab_rooms_response.status_code = 200
    lab_rooms_response.json.return_value = {"success": True, "lab_rooms": [201, 202, 203]}
    
    mock_api_client["get"].side_effect = [buildings_response, lab_rooms_response]
    
    response = client.get('/search')
    assert response.status_code == 200
    # Check for elements we expect on the search page
    assert b'Search' in response.data
    assert b'Chemical Name' in response.data
    assert b'Building 101' in response.data  # From user preferences

def test_search_post(client, mock_session_user, mock_requests_get, mock_api_client, mock_search_results):
    """Test search form submission"""
    with client.session_transaction() as sess:
        sess['user'] = 'testuser'
        sess['role'] = 'technician'
    
    # Configure API responses
    buildings_response = MagicMock()
    buildings_response.status_code = 200
    buildings_response.json.return_value = {"success": True, "buildings": ["Building 101", "Building 102"]}
    
    lab_rooms_response = MagicMock()
    lab_rooms_response.status_code = 200
    lab_rooms_response.json.return_value = {"success": True, "lab_rooms": [201, 202, 203]}
    
    search_response = MagicMock()
    search_response.status_code = 200
    search_response.json.return_value = {"success": True, "results": mock_search_results}
    
    # First get for buildings, second for lab rooms, post for search
    mock_api_client["get"].side_effect = [buildings_response, lab_rooms_response]
    mock_api_client["post"].return_value = search_response
    
    # Submit search form
    form_data = {
        'chemical_name': 'Acetone',
        'building_name': 'Building 101',
        'lab_room': '202',
        'locker': '3',
        'hazard_classification': 'flammable'
    }
    
    response = client.post('/search', data=form_data)
    assert response.status_code == 200
    assert b'Acetone' in response.data
    assert b'67-64-1' in response.data  # CAS number from results
    
    # Check that API was called with correct search parameters
    search_call = mock_api_client["post"].call_args_list[0]
    assert 'chemsearch' in search_call[0][0]
    assert 'Acetone' in str(search_call[1]['json'])
    assert 'Building 101' in str(search_call[1]['json'])
    assert '202' in str(search_call[1]['json'])

def test_sort_results(mock_search_results):
    """Test the sort_results functionality"""
    # Sort by name ascending
    sorted_results = search.sort_results(mock_search_results, 'name', 'asc')
    assert sorted_results[0]['name'] == 'Acetone'
    assert sorted_results[1]['name'] == 'Ethanol'
    
    # Sort by name descending
    sorted_results = search.sort_results(mock_search_results, 'name', 'desc')
    assert sorted_results[0]['name'] == 'Ethanol'
    assert sorted_results[1]['name'] == 'Acetone'
    
    # Sort by quantity ascending
    sorted_results = search.sort_results(mock_search_results, 'qty', 'asc')
    assert sorted_results[0]['quantity'] == 2.5
    assert sorted_results[1]['quantity'] == 5.0
    
    # Sort by quantity descending
    sorted_results = search.sort_results(mock_search_results, 'qty', 'desc')
    assert sorted_results[0]['quantity'] == 5.0
    assert sorted_results[1]['quantity'] == 2.5

def test_chemical_details_authenticated(client, mock_session_user, mock_requests_get, mock_api_client, mock_chemical_details):
    """Test viewing chemical details with authenticated user"""
    with client.session_transaction() as sess:
        sess['user'] = 'testuser'
        sess['role'] = 'technician'
    
    # Configure API response for chemical details
    chemical_response = MagicMock()
    chemical_response.status_code = 200
    chemical_response.json.return_value = {"success": True, "chemical": mock_chemical_details}
    
    mock_api_client["get"].return_value = chemical_response
    
    response = client.get('/search/chemical/1')
    assert response.status_code == 200
    assert b'Acetone' in response.data
    assert b'67-64-1' in response.data  # CAS number
    assert b'C3H6O' in response.data  # Chemical formula

def test_chemical_details_unauthenticated(client, mock_api_client):
    """Test viewing chemical details with unauthenticated user"""
    response = client.get('/search/chemical/1')
    # Should redirect to login
    assert response.status_code >= 300 and response.status_code < 400
    # Skip location check if it's not available
    if hasattr(response, 'location'):
        assert '/login' in response.location or 'login' in response.location

def test_receive_material(client, mock_session_user, mock_requests_get, mock_api_client, mock_chemical_details):
    """Test the receive material form"""
    with client.session_transaction() as sess:
        sess['user'] = 'testuser'
        sess['role'] = 'technician'
    
    # Configure API response for chemical details
    chemical_response = MagicMock()
    chemical_response.status_code = 200
    chemical_response.json.return_value = {"success": True, "chemical": mock_chemical_details}
    
    mock_api_client["get"].return_value = chemical_response
    
    form_data = {
        'scroll_position': '100'
    }
    
    response = client.post('/search/chemical/1/receive', data=form_data)
    assert response.status_code == 200
    assert b'Receive Material' in response.data
    assert b'Acetone' in response.data
    assert b'Add' in response.data  # Action button text

def test_checkout_material(client, mock_session_user, mock_requests_get, mock_api_client, mock_chemical_details):
    """Test the checkout material form"""
    with client.session_transaction() as sess:
        sess['user'] = 'testuser'
        sess['role'] = 'technician'
    
    # Configure API response for chemical details
    chemical_response = MagicMock()
    chemical_response.status_code = 200
    chemical_response.json.return_value = {"success": True, "chemical": mock_chemical_details}
    
    mock_api_client["get"].return_value = chemical_response
    
    form_data = {
        'scroll_position': '100'
    }
    
    response = client.post('/search/chemical/1/checkout', data=form_data)
    assert response.status_code == 200
    assert b'Check Out Material' in response.data
    assert b'Acetone' in response.data
    assert b'Remove' in response.data  # Action button text

def test_update_inventory(client, mock_session_user, mock_api_client, mock_chemical_details):
    """Test updating inventory quantity"""
    with client.session_transaction() as sess:
        sess['user'] = 'testuser'
        sess['role'] = 'technician'
        sess['search_results'] = [
            {"id": 1, "name": "Acetone", "quantity": 2.5},
            {"id": 2, "name": "Ethanol", "quantity": 5.0}
        ]
    
    # Configure API responses
    update_response = MagicMock()
    update_response.status_code = 200
    update_response.json.return_value = {"success": True, "new_quantity": 3.5}
    
    mock_api_client["post"].return_value = update_response
    
    form_data = {
        'action': 'add',
        'quantity': '1.0',
        'scroll_position': '100'
    }
    
    response = client.post('/search/chemical/1/update_inventory', data=form_data, follow_redirects=True)
    assert response.status_code == 200 or response.status_code == 302  # Accept either success or redirect
    
    # Verify API client was called with correct data
    update_call = mock_api_client["post"].call_args_list[0]
    assert 'update_inventory' in update_call[0][0]
    assert "'inventory_id': 1" in str(update_call[1]['json'])
    assert "'quantity': 1.0" in str(update_call[1]['json'])
    assert "'action': 'add'" in str(update_call[1]['json'])
    
    # Check session was updated with new quantity
    with client.session_transaction() as sess:
        search_results = sess.get('search_results', [])
        for item in search_results:
            if item['id'] == 1:
                assert item['quantity'] == 3.5

def test_update_inventory_invalid_quantity(client, mock_session_user, mock_requests_get, mock_api_client, mock_chemical_details):
    """Test updating inventory with invalid quantity"""
    with client.session_transaction() as sess:
        sess['user'] = 'testuser'
        sess['role'] = 'technician'
    
    # Configure API response for chemical details (needed for error rendering)
    chemical_response = MagicMock()
    chemical_response.status_code = 200
    chemical_response.json.return_value = {"success": True, "chemical": mock_chemical_details}
    
    mock_api_client["get"].return_value = chemical_response
    
    form_data = {
        'action': 'add',
        'quantity': '-1.0',  # Invalid negative quantity
        'scroll_position': '100'
    }
    
    response = client.post('/search/chemical/1/update_inventory', data=form_data)
    assert response.status_code == 200
    assert b'Quantity must be greater than zero' in response.data

def test_get_shared_header_success(mock_requests_get):
    """Test successfully getting shared header"""
    header = search.get_shared_header("testuser", True)
    assert "Test Header" in header
    mock_requests_get.assert_called_once()

def test_get_shared_header_failure(mock_requests_get):
    """Test fallback when shared header fails"""
    # Configure the mock to simulate a failure
    mock_requests_get.side_effect = Exception("Connection error")
    
    header = search.get_shared_header("testuser", True)
    assert "ChemTrack Search (Error Header)" in header
    assert "testuser" in header

def test_get_shared_navigation_success(mock_requests_get):
    """Test successfully getting shared navigation"""
    nav = search.get_shared_navigation("technician", "search")
    assert "Test Navigation" in nav
    mock_requests_get.assert_called_once()

def test_get_shared_navigation_failure(mock_requests_get):
    """Test fallback when shared navigation fails"""
    # Configure the mock to simulate a failure
    mock_requests_get.side_effect = Exception("Connection error")
    
    nav = search.get_shared_navigation("technician", "search")
    assert "Search (Error)" in nav

def test_get_buildings_success(mock_api_client):
    """Test successfully getting buildings list"""
    # Configure API response for buildings
    buildings_response = MagicMock()
    buildings_response.status_code = 200
    buildings_response.json.return_value = {"success": True, "buildings": ["Building 101", "Building 102"]}
    
    mock_api_client["get"].return_value = buildings_response
    
    buildings = search.get_buildings()
    assert len(buildings) == 2
    assert "Building 101" in buildings
    assert "Building 102" in buildings

def test_get_buildings_failure(mock_api_client):
    """Test handling failure when getting buildings"""
    # Configure API response for buildings to return failure
    buildings_response = MagicMock()
    buildings_response.status_code = 500
    
    mock_api_client["get"].return_value = buildings_response
    
    buildings = search.get_buildings()
    assert buildings == []

def test_get_lab_rooms_success(mock_api_client):
    """Test successfully getting lab rooms for a building"""
    # Configure API response for lab rooms
    lab_rooms_response = MagicMock()
    lab_rooms_response.status_code = 200
    lab_rooms_response.json.return_value = {"success": True, "lab_rooms": [201, 202, 203]}
    
    mock_api_client["get"].return_value = lab_rooms_response
    
    lab_rooms = search.get_lab_rooms("Building 101")
    assert len(lab_rooms) == 3
    assert 201 in lab_rooms
    assert 202 in lab_rooms
    assert 203 in lab_rooms

def test_get_lab_rooms_failure(mock_api_client):
    """Test handling failure when getting lab rooms"""
    # Configure API response for lab rooms to return failure
    lab_rooms_response = MagicMock()
    lab_rooms_response.status_code = 500
    
    mock_api_client["get"].return_value = lab_rooms_response
    
    lab_rooms = search.get_lab_rooms("Building 101")
    assert lab_rooms == []

def test_get_lab_rooms_empty_building(mock_api_client):
    """Test getting lab rooms with empty building name"""
    lab_rooms = search.get_lab_rooms("")
    assert lab_rooms == []
    # API client should not be called
    mock_api_client["get"].assert_not_called()

def test_logout(client):
    """Test the logout route"""
    response = client.get('/logout')
    # Should redirect
    assert response.status_code >= 300 and response.status_code < 400

def test_health_endpoint(client):
    """Test the health check endpoint"""
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["status"] == "healthy"

def test_test_chemical_route(client):
    """Test the test chemical route"""
    response = client.get('/search/chemical/test')
    assert response.status_code == 200
    assert b'Chemical test route working correctly!' in response.data
