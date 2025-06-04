import os
import time
import logging
from flask import Flask, render_template, request, redirect, session, jsonify
import requests

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
    PRC_BACKEND = 'https://' + BASE_URL
    PRC_LOGIN = ''
    PRC_SEARCH = ''
    PRC_SHARED = 'https://' + BASE_URL
    PRC_STATIC = ''
    PRC_MAIN = ''
else:
    PRC_BACKEND = 'http://ct-backend:8000'
    PRC_LOGIN = 'http://localhost:8001'
    PRC_SEARCH = 'http://localhost:8004'
    PRC_SHARED = 'http://ct-shared-templates:8000'
    PRC_STATIC = 'http://localhost:8002'
    PRC_MAIN = 'http://localhost:8003'

# Ensure URLs have proper scheme for requests
logger.info(f'Base URL = {BASE_URL}')
logger.info(f'Backend Process: {PRC_BACKEND}')
logger.info(f'Shared Process: {PRC_SHARED}')
logger.info(f'Static Process: {PRC_STATIC}')
logger.info(f'Login Process: {PRC_LOGIN}')
logger.info(f'Main Process: {PRC_MAIN}')

# Middleware to track request metrics
@app.before_request
def before_request():
    request.start_time = time.time()

@app.after_request
def after_request(response):
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

def get_shared_navigation(role, active_page):
    """Get the shared navigation from the shared-templates service"""
    try:
        logger.info(f'User role: {role}')
        params = {
            'role': role,
            'active_page': active_page,
            'search_url': PRC_SEARCH + "/search"
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

@app.route('/recipes')
def index():
    # Check if user has a valid session
    if 'user' not in session:
        return redirect('/login')
    
    # Check user role - inventory-taker should not access this page
    role = session.get('role', '')
    if role == 'inventory-taker' or role not in ['technician', 'manager', 'administrator']:
        return redirect(PRC_MAIN + '/')
    
    # Get shared header and navigation
    username = session.get('user', '')
    header_html = get_shared_header(username, True)
    navigation_html = get_shared_navigation(role, 'recipes')
    
    # User has a valid session, render the recipes page
    return render_template('recipes.html', 
                          username=username,
                          role=role,
                          static_url=PRC_STATIC + "/static",
                          search_url=PRC_SEARCH + "/search",
                          header_html=header_html,
                          navigation_html=navigation_html)

@app.route('/logout')
def logout():
    # Clear the user session
    session.pop('user', None)
    session.pop('role', None)
                
    # Clear session
    keys_to_remove = [key for key in session.keys()]
    for key in keys_to_remove:
        session.pop(key, None)

    # Redirect to the login service
    return redirect(PRC_LOGIN + "/login")

@app.route('/login')
def login_redirect():
    # Clear the user session
    session.pop('user', None)
    session.pop('role', None)
    # Redirect to the login service
    return redirect(PRC_LOGIN + "/login")

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
