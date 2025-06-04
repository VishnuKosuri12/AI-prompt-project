import os
import time
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, abort, Response
import requests
import logging
import api_client

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create Flask WSGI application
app = Flask(__name__, static_folder=None)  # Disable static folder as it's served by nginx

# Secret key for session encryption - in production, this would be loaded from environment variables
app.secret_key = os.environ.get('SECRET_KEY', 'dev_secret_key')

# Get the application URLs
BASE_URL = os.environ.get('BASE_URL')
if "chemtrack" in BASE_URL:
    PRC_BACKEND = 'https://chemtrack.767397980456.aws.glpoly.net'
    PRC_LOGIN = ''
    PRC_MAIN = 'https://chemtrack.767397980456.aws.glpoly.net'
    PRC_SHARED = 'https://chemtrack.767397980456.aws.glpoly.net'
    PRC_STATIC = ''
    PRC_RECIPES = ''
else:
    PRC_BACKEND = 'http://ct-backend:8000'
    PRC_LOGIN = 'http://localhost:8001'
    PRC_MAIN = 'http://localhost:8003'
    PRC_SHARED = 'http://ct-shared-templates:8000'
    PRC_STATIC = 'http://localhost:8002'
    PRC_RECIPES = 'http://localhost:8007'

logger.info(f'Backend API URL: {PRC_BACKEND}')
logger.info(f'Static Content URL: {PRC_STATIC}')
logger.info(f'Login URL: {PRC_LOGIN}')
logger.info(f'Main URL: {PRC_MAIN}')


# Middleware to track request metrics
@app.before_request
def before_request():
    request.start_time = time.time()

@app.after_request
def after_request(response):
    request_latency = time.time() - request.start_time   
    return response

def get_buildings():
    """Get list of buildings from backend API"""
    try:
        buildings_endpoint = f"{PRC_BACKEND}/backend/buildings"
        response = api_client.get(buildings_endpoint, timeout=8)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                return result.get('buildings', [])
        return []
    except Exception as e:
        logger.error(str(e))
        return []

def get_lab_rooms(building_name):
    """Get list of lab rooms for a specific building from backend API"""
    if not building_name:
        return []
        
    try:
        lab_rooms_endpoint = f"{PRC_BACKEND}/backend/lab_rooms/{building_name}"
        response = api_client.get(lab_rooms_endpoint, timeout=8)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                return result.get('lab_rooms', [])
        return []
    except Exception as e:
        logger.error(str(e))
        return []

def get_shared_header(username, user_account_enabled=False):
    """Get the shared header from the shared-templates service"""
    try:
        params = {
            'username': username,
            'static_url': PRC_STATIC + '/static',
            'user_account_enabled': str(user_account_enabled).lower()
        }
        #logger.debug(f"[SEARCH] Fetching header from: {PRC_SHARED}/shared-templates/header with params: {params}")
        response = requests.get(f"{PRC_SHARED}/shared-templates/header", params=params, timeout=5)
        if response.status_code == 200:
            header_html = response.text
            logger.debug(f"[SEARCH] Successfully fetched header HTML")
            return header_html
        else:
            logger.error(f"[SEARCH] Error fetching shared header: {response.status_code}, {response.text}")
            # Fallback header for debugging
            return f"""
            <header class="header">
                <div class="header-left">
                    <h1 class="header-title">ChemTrack Search (Fallback Header)</h1>
                </div>
                <div class="header-user">
                    <span class="header-user-name">{username}</span>
                    <a href="/logout" class="logout-btn">Logout</a>
                </div>
            </header>
            """
    except Exception as e:
        logger.error(f"[SEARCH] Exception fetching shared header: {str(e)}")
        # Fallback header for debugging
        return f"""
        <header class="header">
            <div class="header-left">
                <h1 class="header-title">ChemTrack Search (Error Header)</h1>
            </div>
            <div class="header-user">
                <span class="header-user-name">{username}</span>
                <a href="/logout" class="logout-btn">Logout</a>
            </div>
        </header>
        """

def get_shared_navigation(role, active_page):
    """Get the shared navigation from the shared-templates service"""
    try:
        params = {
            'role': role,
            'active_page': active_page,
            'search_url': '/search',
            'recipes_url': PRC_RECIPES
        }
        #logger.debug(f"[SEARCH] Fetching navigation from: {PRC_SHARED}/shared-templates/navigation with params: {params}")
        response = requests.get(f"{PRC_SHARED}/shared-templates/navigation", params=params, timeout=5)
        if response.status_code == 200:
            nav_html = response.text
            logger.debug(f"[SEARCH] Successfully fetched navigation HTML")
            return nav_html
        else:
            logger.error(f"[SEARCH] Error fetching shared navigation: {response.status_code}, {response.text}")
            # Fallback navigation for debugging
            return """
            <nav class="nav-sidebar">
                <ul class="nav-list">
                    <li class="nav-item">
                        <a href="/" class="nav-link">
                            <span class="nav-icon">🏠</span>
                            Home (Fallback)
                        </a>
                    </li>
                    <li class="nav-item">
                        <a href="/search" class="nav-link active">
                            <span class="nav-icon">🔍</span>
                            Search (Fallback)
                        </a>
                    </li>
                </ul>
            </nav>
            """
    except Exception as e:
        logger.error(f"[SEARCH] Exception fetching shared navigation: {str(e)}")
        # Fallback navigation for debugging
        return """
        <nav class="nav-sidebar">
            <ul class="nav-list">
                <li class="nav-item">
                    <a href="/" class="nav-link">
                        <span class="nav-icon">🏠</span>
                        Home (Error)
                    </a>
                </li>
                <li class="nav-item">
                    <a href="/search" class="nav-link active">
                        <span class="nav-icon">🔍</span>
                        Search (Error)
                    </a>
                </li>
            </ul>
        </nav>
        """

# Log registered routes
logger.info("Registered routes:")
for rule in app.url_map.iter_rules():
    logger.info(f"Route: {rule.rule} Methods: {rule.methods}")

@app.route('/search/chemical/test')
def test_chemical_route():
    """Test route for chemical details"""
    logger.info("Test chemical route accessed")
    return "Chemical test route working correctly!"

@app.route('/search/chemical/<int:chemical_id>', methods=['GET'])
def chemical_details(chemical_id):
    """Display details for a specific chemical"""
    logger.info(f"Accessing chemical details for ID: {chemical_id}")
    
    # Check if user has a valid session
    if 'user' not in session:
        logger.warning("No user session found, redirecting to login")
        return redirect('/login')
    
    # Get the scroll position from the query parameters
    scroll_position = request.args.get('scroll_position', '0')
    logger.info(f"Scroll position: {scroll_position}")
    
    # Get chemical details from backend
    try:
        chemical_endpoint = f"{PRC_BACKEND}/backend/chemical/{chemical_id}"
        response = api_client.get(chemical_endpoint, timeout=8)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                chemical = result.get('chemical', {})
                
                # Get shared header and navigation
                username = session.get('user', '')
                role = session.get('role', '')
                header_html = get_shared_header(username, True)
                navigation_html = get_shared_navigation(role, 'search')
                
                return render_template('chemical_details.html',
                                      username=username,
                                      role=role,
                                      static_url=PRC_STATIC + '/static',
                                      chemical=chemical,
                                      scroll_position=scroll_position,
                                      header_html=header_html,
                                      navigation_html=navigation_html,
                                      show_inventory_form=False)
            else:
                logger.error(f"Failed to get chemical details: {result.get('message')}")
                return redirect('/search')
        else:
            logger.error(f"Backend API error: {response.status_code} - {response.text}")
            return redirect('/search')
    except Exception as e:
        logger.error(f"Error getting chemical details: {str(e)}")
        return redirect('/search')

@app.route('/search/chemical/<int:chemical_id>/receive', methods=['POST'])
def receive_material(chemical_id):
    """Show form to receive material"""
    # Check if user has a valid session
    if 'user' not in session:
        return redirect('/login')
    
    # Get the scroll position from the form
    scroll_position = request.form.get('scroll_position', '0')
    
    try:
        # Get chemical details from backend
        chemical_endpoint = f"{PRC_BACKEND}/backend/chemical/{chemical_id}"
        response = api_client.get(chemical_endpoint, timeout=8)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                chemical = result.get('chemical', {})
                
                # Get shared header and navigation
                username = session.get('user', '')
                role = session.get('role', '')
                header_html = get_shared_header(username, True)
                navigation_html = get_shared_navigation(role, 'search')
                
                return render_template('chemical_details.html',
                                      username=username,
                                      role=role,
                                      static_url=PRC_STATIC + '/static',
                                      chemical=chemical,
                                      scroll_position=scroll_position,
                                      header_html=header_html,
                                      navigation_html=navigation_html,
                                      show_inventory_form=True,
                                      action_title="Receive Material",
                                      action="add",
                                      action_button="Add",
                                      error=None)
            else:
                logger.error(f"Failed to get chemical details: {result.get('message')}")
                return redirect('/search')
        else:
            logger.error(f"Backend API error: {response.status_code} - {response.text}")
            return redirect('/search')
    except Exception as e:
        logger.error(f"Error getting chemical details: {str(e)}")
        return redirect('/search')

@app.route('/search/chemical/<int:chemical_id>/checkout', methods=['POST'])
def checkout_material(chemical_id):
    """Show form to checkout material"""
    # Check if user has a valid session
    if 'user' not in session:
        return redirect('/login')
    
    # Get the scroll position from the form
    scroll_position = request.form.get('scroll_position', '0')
    
    try:
        # Get chemical details from backend
        chemical_endpoint = f"{PRC_BACKEND}/backend/chemical/{chemical_id}"
        response = api_client.get(chemical_endpoint, timeout=8)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                chemical = result.get('chemical', {})
                
                # Get shared header and navigation
                username = session.get('user', '')
                role = session.get('role', '')
                header_html = get_shared_header(username, True)
                navigation_html = get_shared_navigation(role, 'search')
                
                return render_template('chemical_details.html',
                                      username=username,
                                      role=role,
                                      static_url=PRC_STATIC + '/static',
                                      chemical=chemical,
                                      scroll_position=scroll_position,
                                      header_html=header_html,
                                      navigation_html=navigation_html,
                                      show_inventory_form=True,
                                      action_title="Check Out Material",
                                      action="remove",
                                      action_button="Remove",
                                      error=None)
            else:
                logger.error(f"Failed to get chemical details: {result.get('message')}")
                return redirect('/search')
        else:
            logger.error(f"Backend API error: {response.status_code} - {response.text}")
            return redirect('/search')
    except Exception as e:
        logger.error(f"Error getting chemical details: {str(e)}")
        return redirect('/search')

@app.route('/search/chemical/<int:chemical_id>/update_inventory', methods=['POST'])
def update_chemical_inventory(chemical_id):
    """Update inventory quantity"""
    # Check if user has a valid session
    if 'user' not in session:
        return redirect('/login')
    
    # Get form data
    action = request.form.get('action')
    quantity = request.form.get('quantity')
    scroll_position = request.form.get('scroll_position', '0')
    
    # Validate form data
    if not action or action not in ['add', 'remove']:
        return render_error(chemical_id, "Invalid action", scroll_position)
    
    try:
        quantity = float(quantity)
        if quantity <= 0:
            return render_error(chemical_id, "Quantity must be greater than zero", scroll_position)
    except ValueError:
        return render_error(chemical_id, "Invalid quantity value", scroll_position)
    
    # Call backend API to update inventory
    try:
        update_endpoint = f"{PRC_BACKEND}/backend/update_inventory"
        update_data = {
            "inventory_id": chemical_id,
            "quantity": quantity,
            "action": action
        }
        
        logger.info(f"Sending inventory update to backend: {update_data}")
        
        response = api_client.post(update_endpoint, json=update_data, timeout=10)
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                # Update the inventory quantity in session cache if available
                if 'search_results' in session:
                    search_results = session.get('search_results', [])
                    for item in search_results:
                        if item['id'] == chemical_id:
                            item['quantity'] = float(result.get('new_quantity', 0))
                    session['search_results'] = search_results
                
                # Redirect to the chemical details page with a success message
                return redirect(f"/search/chemical/{chemical_id}?scroll_position={scroll_position}")
            else:
                error_message = result.get('message', 'Failed to update inventory')
                return render_error(chemical_id, error_message, scroll_position)
        else:
            error_message = "Failed to update inventory"
            try:
                error_data = response.json()
                if 'detail' in error_data:
                    error_message = error_data['detail']
            except Exception:
                error_message = f"Server error ({response.status_code})"
                
            return render_error(chemical_id, error_message, scroll_position)
    except Exception as e:
        logger.error(f"Error updating inventory: {str(e)}")
        return render_error(chemical_id, f"Error updating inventory: {str(e)}", scroll_position)

def render_error(chemical_id, error_message, scroll_position):
    """Helper function to render chemical details with error message"""
    try:
        # Get chemical details from backend
        chemical_endpoint = f"{PRC_BACKEND}/backend/chemical/{chemical_id}"
        response = api_client.get(chemical_endpoint, timeout=8)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                chemical = result.get('chemical', {})
                
                # Get shared header and navigation
                username = session.get('user', '')
                role = session.get('role', '')
                header_html = get_shared_header(username, True)
                navigation_html = get_shared_navigation(role, 'search')
                
                # Determine which form we were processing based on the action
                action = request.form.get('action', '')
                if action == 'add':
                    action_title = "Receive Material"
                    action_button = "Add"
                else:
                    action_title = "Check Out Material"
                    action_button = "Remove"
                
                return render_template('chemical_details.html',
                                      username=username,
                                      role=role,
                                      static_url=PRC_STATIC + '/static',
                                      chemical=chemical,
                                      scroll_position=scroll_position,
                                      header_html=header_html,
                                      navigation_html=navigation_html,
                                      show_inventory_form=True,
                                      action_title=action_title,
                                      action=action,
                                      action_button=action_button,
                                      error=error_message)
    except Exception as e:
        logger.error(f"Error rendering error page: {str(e)}")
    
    # If everything else fails, redirect to search
    return redirect('/search')

@app.route('/search', methods=['GET', 'POST'])
def search():
    # Check if user has a valid session
    if 'user' not in session:
        return redirect('/login')
    
    # Initialize variables
    search_results = []
    error = None
    sort_column = request.args.get('sort', 'name')  # Default sort by name
    sort_direction = request.args.get('direction', 'asc')  # Default ascending
    scroll_position = request.form.get('scroll_position', request.args.get('scroll_position', '0'))
    
    # Initialize filter values from session or user preferences
    chemical_name = session.get('filter_chemical_name', '')
    hazard_classification = session.get('filter_hazard_classification', '')
    
    # Use user preferences for building and lab room if available and no filter is set
    building_name = session.get('filter_building_name', '')
    if not building_name and 'pref_building' in session:
        building_name = session.get('pref_building', '')
    logger.debug(f'pref building name: {building_name}')
    
    lab_room = session.get('filter_lab_room', '')
    if not lab_room and 'pref_lab_room' in session:
        lab_room = session.get('pref_lab_room', '')
    
    locker = session.get('filter_locker', '')
    
    # Get building list for dropdown
    buildings = get_buildings()
    
    # Get lab rooms for selected building
    lab_rooms = get_lab_rooms(building_name) if building_name else []
    
    # Process search form submission
    if request.method == 'POST':
        try:
            # Get search parameters from form
            chemical_name = request.form.get('chemical_name', '')
            building_name = request.form.get('building_name', '')
            lab_room = request.form.get('lab_room', '')
            locker = request.form.get('locker', '')
            hazard_classification = request.form.get('hazard_classification', '')
            
            # Store filter values in session
            session['filter_chemical_name'] = chemical_name
            session['filter_building_name'] = building_name
            session['filter_lab_room'] = lab_room
            session['filter_locker'] = locker
            session['filter_hazard_classification'] = hazard_classification
            
            # Convert numeric fields if provided
            lab_room_number = int(lab_room) if lab_room and lab_room.isdigit() else None
            locker_number = int(locker) if locker and locker.isdigit() else None
            
            # Prepare search request
            search_endpoint = f"{PRC_BACKEND}/backend/chemsearch"
            search_data = {
                "name": chemical_name if chemical_name else None,
                "building_name": building_name if building_name else None,
                "lab_room_number": lab_room_number,
                "locker_number": locker_number,
                "hazard_classification": hazard_classification if hazard_classification else None
            }
            
            # Remove None values for cleaner request
            search_data = {k: v for k, v in search_data.items() if v is not None}
            
            logger.debug(f"Connecting to backend API at: {search_endpoint}")
            logger.debug(f"Search data: {search_data}")
            
            # Call the backend API with API key
            response = api_client.post(search_endpoint, json=search_data, timeout=8)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    search_results = result.get('results', [])
                    # Store search results in session for later sorting
                    session['search_results'] = search_results
                else:
                    error = result.get('message', 'Search failed')
            else:
                error = f"Search service unavailable (Status code: {response.status_code})"
                logger.error(f"Backend API error: {response.text}")
                
        except Exception as e:
            error = "Could not connect to search service"
            logger.error(f"Connection error: {str(e)}")
    
    # For GET requests with sort parameters, retrieve results from session and apply local sorting
    elif request.method == 'GET' and 'search_results' in session:
        search_results = session.get('search_results', [])
        if search_results and (sort_column or sort_direction):
            search_results = sort_results(search_results, sort_column, sort_direction)
    
    # Get shared header and navigation
    username = session.get('user', '')
    role = session.get('role', '')
    logger.debug(f"[DEBUG] Fetching header for username: {username}")
    header_html = get_shared_header(username, True)
    logger.debug(f"[DEBUG] Header HTML length: {len(header_html)}")
    logger.debug(f"[DEBUG] Fetching navigation for role: {role}, active_page: search")
    navigation_html = get_shared_navigation(role, 'search')
    logger.debug(f"[DEBUG] Navigation HTML length: {len(navigation_html)}")
    
    # Render the search page with results (if any)
    # Convert search results to JSON for the client-side
    import json
    chemicals_json = json.dumps(search_results) if search_results else "[]"
    
    return render_template('search.html',
                          username=username,
                          role=role,
                          static_url=PRC_STATIC + '/static',
                          results=search_results,
                          chemicals_json=chemicals_json,  # Pass pre-converted JSON string
                          error=error,
                          sort_column=sort_column,
                          sort_direction=sort_direction,
                          chemical_name=chemical_name,
                          building_name=building_name,
                          lab_room=lab_room,
                          locker=locker,
                          hazard_classification=hazard_classification,
                          buildings=buildings,
                          lab_rooms=lab_rooms,
                          header_html=header_html,
                          navigation_html=navigation_html)

def sort_results(results, column, direction):
    """Sort search results by the specified column and direction"""
    reverse = direction.lower() == 'desc'
    
    # Map column names to their keys in the results
    column_map = {
        'name': 'name',
        'uom': 'unit_of_measure',
        'qty': 'quantity',
        'reorder_qty': 'reorder_quantity',
        'bld_name': 'building_name',
        'lab_room': 'lab_room_number',
        'locker': 'locker_number',
        'cas_number': 'cas_number',
        'chemical_formula': 'chemical_formula',
        'signal_word': 'signal_word',
        'physical_state': 'physical_state'
    }
    
    # Get the actual key to sort by
    sort_key = column_map.get(column, 'name')
    
    # Sort the results
    return sorted(results, key=lambda x: x.get(sort_key, ''), reverse=reverse)

@app.route('/search/get_lab_rooms')
def get_lab_rooms_ajax():
    """AJAX endpoint to get lab rooms for a building"""
    building_name = request.args.get('building')
    logger.info(f"AJAX request for lab rooms with building: {building_name}")
    
    if not building_name:
        logger.warning("No building name provided in request")
        return jsonify({"success": False, "lab_rooms": []})
    
    lab_rooms = get_lab_rooms(building_name)
    logger.info(f"Returning lab rooms for {building_name}: {lab_rooms}")
    return jsonify({"success": True, "lab_rooms": lab_rooms})

@app.route('/logout')
def logout():
    return redirect(PRC_MAIN + '/logout')

@app.route('/')
def index():
    # Check if user has a valid session
    if 'user' not in session:
        return redirect('/login')
    
    # Redirect to the main page
    return redirect(PRC_MAIN + '/main')

@app.route('/update_inventory', methods=['POST'])
def update_inventory():
    """API endpoint to update inventory quantity"""
    # Check if user has a valid session
    if 'user' not in session:
        logger.error("Update inventory failed: No user session")
        return jsonify({"success": False, "message": "Authentication required"}), 401
    
    try:
        # Parse JSON request
        data = request.get_json()
        if not data:
            logger.error("Update inventory failed: Missing request data")
            return jsonify({"success": False, "message": "Missing request data"}), 400
        
        inventory_id = data.get('inventory_id')
        quantity = data.get('quantity')
        action = data.get('action')
        
        # Log request details for debugging
        logger.info(f"Update inventory request: id={inventory_id}, qty={quantity}, action={action}")
        
        # Validate required fields
        if not inventory_id or not quantity or not action:
            logger.error(f"Update inventory failed: Missing required fields - id={inventory_id}, qty={quantity}, action={action}")
            return jsonify({"success": False, "message": "Missing required fields"}), 400
            
        # Validate action type
        if action not in ['add', 'remove']:
            logger.error(f"Update inventory failed: Invalid action type - {action}")
            return jsonify({"success": False, "message": "Invalid action type"}), 400
            
        # Validate quantity is positive
        try:
            quantity = float(quantity)
            if quantity <= 0:
                logger.error(f"Update inventory failed: Invalid quantity - {quantity}")
                return jsonify({"success": False, "message": "Quantity must be greater than zero"}), 400
        except ValueError:
            logger.error(f"Update inventory failed: Non-numeric quantity - {quantity}")
            return jsonify({"success": False, "message": "Invalid quantity value"}), 400
            
        # Call backend API to update inventory
        update_endpoint = f"{PRC_BACKEND}/backend/update_inventory"
        update_data = {
            "inventory_id": inventory_id,
            "quantity": quantity,
            "action": action
        }
        
        logger.info(f"Sending inventory update to backend: {update_data}")
        logger.info(f"Backend endpoint: {update_endpoint}")
        
        try:
            response = api_client.post(update_endpoint, json=update_data, timeout=10)
            logger.info(f"Backend response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Inventory update response: {result}")
                
                # If successful, update the inventory quantity in session cache
                if result.get('success') and 'search_results' in session:
                    search_results = session.get('search_results', [])
                    for item in search_results:
                        if item['id'] == inventory_id:
                            item['quantity'] = float(result.get('new_quantity', 0))
                    
                    session['search_results'] = search_results
                    
                return jsonify(result)
            else:
                error_message = "Failed to update inventory"
                try:
                    error_data = response.json()
                    logger.error(f"Backend error response: {error_data}")
                    if 'detail' in error_data:
                        error_message = error_data['detail']
                except Exception as parse_e:
                    logger.error(f"Could not parse error response: {str(parse_e)}")
                    logger.error(f"Raw response: {response.text}")
                
                logger.error(f"Update inventory failed with status {response.status_code}: {error_message}")
                return jsonify({"success": False, "message": error_message}), response.status_code
        except requests.exceptions.Timeout:
            logger.error("Backend request timed out")
            return jsonify({"success": False, "message": "Request to backend timed out"}), 504
        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error to backend at {update_endpoint}")
            return jsonify({"success": False, "message": "Could not connect to backend service"}), 503
                
    except Exception as e:
        logger.error(f"Error updating inventory: {str(e)}", exc_info=True)
        return jsonify({"success": False, "message": f"Error updating inventory: {str(e)}"}), 500

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
