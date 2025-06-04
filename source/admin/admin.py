import os
import time
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, Response
import requests
import logging
import api_client

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create Flask WSGI application
app = Flask(__name__, static_folder=None)  # Disable static folder as it's served by nginx

# Secret key for session encryption - in production, this would be loaded from environment variables
app.secret_key = os.environ.get('SECRET_KEY', 'dev_secret_key')

# Get the application URLs
BASE_URL = os.environ.get('BASE_URL')
if "chemtrack" in BASE_URL:
    PRC_BACKEND = 'https://chemtrack.767397980456.aws.glpoly.net'
    PRC_MAIN = ''
    PRC_SHARED = 'https://chemtrack.767397980456.aws.glpoly.net'
    PRC_STATIC = ''
    PRC_RECIPES = ''
else:
    PRC_BACKEND = 'http://ct-backend:8000'
    PRC_MAIN = 'http://localhost:8003'
    PRC_SHARED = 'http://ct-shared-templates:8000'
    PRC_STATIC = 'http://localhost:8002'
    PRC_RECIPES = 'http://localhost:8007'

# Ensure URLs have proper scheme for requests
logger.info(f'Base URL = {BASE_URL}')
logger.info(f'Backend Process: {PRC_BACKEND}')
logger.info(f'Shared Process: {PRC_SHARED}')
logger.info(f'Static Process: {PRC_STATIC}')


# Middleware to track request metrics
@app.before_request
def before_metrics_request():
    request.start_time = time.time()

@app.after_request
def after_metrics_request(response):
    request_latency = time.time() - request.start_time
    return response

def get_shared_header(username, user_account_enabled=True):
    """Get the shared header from the shared-templates service"""
    try:
        params = {
            'username': username,
            'static_url': PRC_STATIC + "/static",
            'user_account_enabled': str(user_account_enabled).lower()
        }
        
        response = requests.get(f"{PRC_SHARED}/shared-templates/header", params=params, timeout=5)
        if response.status_code == 200:
            header_html = response.text
            return header_html
        else:
            logger.error(f"Error fetching shared header: {response.status_code}, {response.text}")
            # Fallback header for debugging
            return f"""
            <header class="header">
                <div class="header-left">
                    <h1 class="header-title">ChemTrack (Fallback Header)</h1>
                </div>
                <div class="header-user">
                    <span class="header-user-name">{username}</span>
                    <a href="/logout" class="logout-btn">Logout</a>
                </div>
            </header>
            """
    except Exception as e:
        logger.error(f"Exception fetching shared header: {str(e)}")
        # Fallback header for debugging
        return f"""
        <header class="header">
            <div class="header-left">
                <h1 class="header-title">ChemTrack (Error Header)</h1>
            </div>
            <div class="header-user">
                <span class="header-user-name">{username}</span>
                <a href="/logout" class="logout-btn">Logout</a>
            </div>
        </header>
        """

def get_shared_navigation(role, active_page, current_path=''):
    """Get the shared navigation from the shared-templates service"""
    try:
        params = {
            'role': role,
            'active_page': active_page,
            'current_path': current_path,
            'main_url': PRC_MAIN,
            'search_url': '/search',
            'recipes_url': PRC_RECIPES
        }
        
        response = requests.get(f"{PRC_SHARED}/shared-templates/navigation", params=params, timeout=5)
        if response.status_code == 200:
            nav_html = response.text
            return nav_html
        else:
            logger.error(f"Error fetching shared navigation: {response.status_code}, {response.text}")
            # Fallback navigation for debugging
            return """
            <nav class="nav-sidebar">
                <ul class="nav-list">
                    <li class="nav-item">
                        <a href="/" class="nav-link active">
                            <span class="nav-icon">🏠</span>
                            Home (Fallback)
                        </a>
                    </li>
                    <li class="nav-item">
                        <a href="/search" class="nav-link">
                            <span class="nav-icon">🔍</span>
                            Search (Fallback)
                        </a>
                    </li>
                </ul>
            </nav>
            """
    except Exception as e:
        logger.error(f"Exception fetching shared navigation: {str(e)}")
        # Fallback navigation for debugging
        return """
        <nav class="nav-sidebar">
            <ul class="nav-list">
                <li class="nav-item">
                    <a href="/" class="nav-link active">
                        <span class="nav-icon">🏠</span>
                        Home (Error)
                    </a>
                </li>
                <li class="nav-item">
                    <a href="/search" class="nav-link">
                        <span class="nav-icon">🔍</span>
                        Search (Error)
                    </a>
                </li>
            </ul>
        </nav>
        """

def check_admin_access():
    """Check if user has admin access (manager or administrator role)"""
    if 'user' not in session:
        return False
    
    role = session.get('role', '')
    return role in ['manager', 'administrator']

@app.before_request
def require_admin_access():
    """Middleware to ensure user has admin access for all admin routes"""
    # Skip for health check route
    if request.path == '/health':
        return None
        
    # Check if user has a valid session
    if 'user' not in session:
        return redirect('/login')
        
    # Check if user has admin access for admin routes
    if not check_admin_access():
        logger.warning(f"Unauthorized access attempt to {request.path} by {session.get('user')}")
        return redirect('/')
        
    return None

@app.route('/admin')
def admin_index():
    """Admin index page"""
    # User has been validated by middleware
    username = session.get('user', '')
    role = session.get('role', '')
    
    # Get shared header and navigation
    header_html = get_shared_header(username, True)
    navigation_html = get_shared_navigation(role, 'admin', request.path)
    
    return render_template('admin_index.html',
                          username=username,
                          role=role,
                          static_url=PRC_STATIC + "/static",
                          header_html=header_html,
                          navigation_html=navigation_html)

@app.route('/admin/users')
def user_management():
    """User management page"""
    username = session.get('user', '')
    role = session.get('role', '')
    
    # Get shared header and navigation
    header_html = get_shared_header(username, True)
    navigation_html = get_shared_navigation(role, 'admin', request.path)
    
    # Get list of users
    try:
        conn = None
        users = []
        error = None
        
        # Get users from backend
        response = api_client.get(f"{PRC_BACKEND}/backend/users")
        if response.status_code == 200:
            users_data = response.json().get('users', [])
            # Process users to ensure preferences are properly formatted
            users = []
            for user in users_data:
                processed_user = {
                    'username': user.get('username', ''),
                    'email': user.get('email', ''),
                    'role': user.get('role', ''),
                    'preferences': {}
                }
                
                # Make sure preferences are properly structured
                if 'preferences' in user and user['preferences']:
                    processed_user['preferences'] = {
                        'building': user['preferences'].get('building', ''),
                        'lab_room': str(user['preferences'].get('lab_room', ''))  # Ensure lab_room is a string
                    }
                    logger.info(f"User {processed_user['username']} preferences: {processed_user['preferences']}")
                
                users.append(processed_user)
        else:
            error = "Failed to fetch users"
            logger.error(f"Error fetching users: {response.text}")
    except Exception as e:
        error = str(e)
        logger.error(f"Exception fetching users: {str(e)}")
        users = []
    
    # Get list of buildings
    try:
        buildings_response = api_client.get(f"{PRC_BACKEND}/backend/buildings")
        buildings = []
        if buildings_response.status_code == 200:
            buildings = buildings_response.json().get('buildings', [])
    except Exception as e:
        buildings = []
        logger.error(f"Error fetching buildings: {str(e)}")
        
    # Get list of roles
    try:
        roles_response = api_client.get(f"{PRC_BACKEND}/backend/roles")
        roles = []
        if roles_response.status_code == 200:
            roles = roles_response.json().get('roles', [])
    except Exception as e:
        roles = []
        logger.error(f"Error fetching roles: {str(e)}")
    
    return render_template('user_management.html',
                          username=username,
                          role=role,
                          users=users,
                          buildings=buildings,
                          roles=roles,
                          error=error,
                          static_url=PRC_STATIC + "/static",
                          backend_url=PRC_BACKEND,
                          header_html=header_html,
                          navigation_html=navigation_html)

@app.route('/admin/locations')
def location_management():
    """Location management page"""
    username = session.get('user', '')
    role = session.get('role', '')
    
    # Get shared header and navigation
    header_html = get_shared_header(username, True)
    navigation_html = get_shared_navigation(role, 'admin', request.path)
    
    # Get list of locations
    try:
        conn = None
        locations = []
        error = None
        
        # Get locations from backend
        response = api_client.get(f"{PRC_BACKEND}/backend/locations")
        if response.status_code == 200:
            locations = response.json().get('locations', [])
        else:
            error = "Failed to fetch locations"
            logger.error(f"Error fetching locations: {response.text}")
    except Exception as e:
        error = str(e)
        logger.error(f"Exception fetching locations: {str(e)}")
        locations = []
    
    # Get list of buildings for filter
    try:
        buildings_response = api_client.get(f"{PRC_BACKEND}/backend/buildings")
        buildings = []
        if buildings_response.status_code == 200:
            buildings = buildings_response.json().get('buildings', [])
    except Exception as e:
        buildings = []
        logger.error(f"Error fetching buildings: {str(e)}")
    
    return render_template('location_management.html',
                          username=username,
                          role=role,
                          locations=locations,
                          buildings=buildings,
                          error=error,
                          static_url=PRC_STATIC + "/static",
                          backend_url=PRC_BACKEND,
                          header_html=header_html,
                          navigation_html=navigation_html)

@app.route('/logout')
def logout():
    """Logout route - clears session and redirects to login"""
    # Clear the user session
    session.pop('user', None)
    session.pop('role', None)
    
    # Clear all session data
    keys_to_remove = [key for key in session.keys()]
    for key in keys_to_remove:
        session.pop(key, None)
        
    # Redirect to login
    return redirect('/login')

@app.route('/admin/lab_rooms/<building>')
def get_lab_rooms(building):
    """Proxy to get lab rooms for a building from the backend"""
    try:
        response = api_client.get(f"{PRC_BACKEND}/backend/lab_rooms/{building}")
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Error fetching lab rooms: {response.text}")
            return jsonify({"success": False, "message": "Failed to fetch lab rooms", "lab_rooms": []})
    except Exception as e:
        logger.error(f"Exception fetching lab rooms: {str(e)}")
        return jsonify({"success": False, "message": str(e), "lab_rooms": []})

@app.route('/admin/create_user', methods=['POST'])
def create_user_proxy():
    """Proxy to create a user via backend"""
    try:
        response = api_client.post(f"{PRC_BACKEND}/backend/createuser", json=request.json)
        return response.json()
    except Exception as e:
        logger.error(f"Exception creating user: {str(e)}")
        return jsonify({"success": False, "message": str(e)})

@app.route('/admin/update_user', methods=['POST'])
def update_user_proxy():
    """Proxy to update a user via backend"""
    try:
        response = api_client.post(f"{PRC_BACKEND}/backend/updateuser", json=request.json)
        return response.json()
    except Exception as e:
        logger.error(f"Exception updating user: {str(e)}")
        return jsonify({"success": False, "message": str(e)})

@app.route('/admin/update_user_preference', methods=['POST'])
def update_user_preference_proxy():
    """Proxy to update a user preference via backend"""
    try:
        response = api_client.post(f"{PRC_BACKEND}/backend/update_user_preference", json=request.json)
        return response.json()
    except Exception as e:
        logger.error(f"Exception updating user preference: {str(e)}")
        return jsonify({"success": False, "message": str(e)})

@app.route('/admin/roles')
def get_roles_proxy():
    """Proxy to get all available roles from backend"""
    try:
        response = api_client.get(f"{PRC_BACKEND}/backend/roles")
        return response.json()
    except Exception as e:
        logger.error(f"Exception fetching roles: {str(e)}")
        return jsonify({"success": False, "message": str(e), "roles": []})

@app.route('/admin/create_location', methods=['POST'])
def create_location_proxy():
    """Proxy to create a location via backend"""
    try:
        response = api_client.post(f"{PRC_BACKEND}/backend/createlocation", json=request.json)
        return response.json()
    except Exception as e:
        logger.error(f"Exception creating location: {str(e)}")
        return jsonify({"success": False, "message": str(e)})

@app.route('/admin/update_location', methods=['POST'])
def update_location_proxy():
    """Proxy to update a location via backend"""
    try:
        response = api_client.post(f"{PRC_BACKEND}/backend/updatelocation", json=request.json)
        return response.json()
    except Exception as e:
        logger.error(f"Exception updating location: {str(e)}")
        return jsonify({"success": False, "message": str(e)})

@app.route('/admin/check_location/<location_id>')
def check_location_proxy(location_id):
    """Proxy to check if a location has inventory via backend"""
    try:
        response = api_client.get(f"{PRC_BACKEND}/backend/checklocation/{location_id}")
        return response.json()
    except Exception as e:
        logger.error(f"Exception checking location: {str(e)}")
        return jsonify({"success": False, "message": str(e), "has_inventory": True})

@app.route('/admin/delete_location/<location_id>', methods=['DELETE'])
def delete_location_proxy(location_id):
    """Proxy to delete a location via backend"""
    try:
        response = api_client.delete(f"{PRC_BACKEND}/backend/deletelocation/{location_id}")
        return response.json()
    except Exception as e:
        logger.error(f"Exception deleting location: {str(e)}")
        return jsonify({"success": False, "message": str(e)})

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
