import os
import time
import boto3
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
    PRC_BACKEND = 'https://' + BASE_URL
    PRC_LOGIN = ''
    PRC_SEARCH = ''
    PRC_SHARED = 'https://' + BASE_URL
    PRC_STATIC = ''
    PRC_RECIPES = ''
else:
    PRC_BACKEND = 'http://ct-backend:8000'
    PRC_BACKEND_BRO = 'http://localhost:8000'
    PRC_LOGIN = 'http://localhost:8001'
    PRC_SEARCH = 'http://localhost:8004'
    PRC_SHARED = 'http://ct-shared-templates:8000'
    PRC_STATIC = 'http://localhost:8002'
    PRC_RECIPES = 'http://localhost:8007'

# Ensure URLs have proper scheme for requests
logger.info(f'Base URL = {BASE_URL}')
logger.info(f'Backend Process: {PRC_BACKEND}')
logger.info(f'Shared Process: {PRC_SHARED}')
logger.info(f'Static Process: {PRC_STATIC}')
logger.info(f'Login Process: {PRC_LOGIN}')

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
        params = {
            'role': role,
            'active_page': active_page,
            'search_url': PRC_SEARCH + "/search",
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

@app.route('/')
def index():
    # Check if user has a valid session
    if 'user' not in session:
        return redirect('/login')
    
    # Get user preferences from session
    user_building = session.get('pref_building', '')
    user_lab_room = session.get('pref_lab_room', '')
    logger.info(f"main index session: {user_building}  {user_lab_room}")
    
    # Get shared header and navigation
    username = session.get('user', '')
    role = session.get('role', '')
    header_html = get_shared_header(username, True)
    navigation_html = get_shared_navigation(role, 'home')
    
    # User has a valid session, render the main page
    return render_template('main.html', 
                          username=username,
                          role=role,
                          user_building=user_building,
                          user_lab_room=user_lab_room,
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

def manage_sns_subscription(email, notification_preference):
    """
    Manages SNS subscription for reorder notification.
    
    Args:
        email: User's email address
        notification_preference: 'on' to subscribe, 'off' to unsubscribe
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # AWS Region
        aws_region = os.environ.get('AWS_REGION', 'us-east-1')
        
        # Create SNS client
        sns_client = boto3.client('sns', region_name=aws_region)
        
        # Get the SNS topic ARN
        # In production, this should come from environment variables or AWS Parameter Store
        sns_topic_arn = f"arn:aws:sns:{aws_region}:{os.environ.get('AWS_ACCOUNT_ID', '767397980456')}:chemtrack-reorder-sns"
        
        if notification_preference == 'on':
            # Subscribe the user to the SNS topic
            response = sns_client.subscribe(
                TopicArn=sns_topic_arn,
                Protocol='email',
                Endpoint=email
            )
            logger.info(f"Subscribed {email} to reorder notifications: {response}")
            return True
        else:
            # Find all subscriptions for this email and unsubscribe
            subscriptions = sns_client.list_subscriptions_by_topic(TopicArn=sns_topic_arn)
            
            for subscription in subscriptions.get('Subscriptions', []):
                if subscription.get('Protocol') == 'email' and subscription.get('Endpoint') == email:
                    subscription_arn = subscription.get('SubscriptionArn')
                    
                    # Make sure it's not "PendingConfirmation"
                    if subscription_arn != 'PendingConfirmation':
                        sns_client.unsubscribe(SubscriptionArn=subscription_arn)
                        logger.info(f"Unsubscribed {email} from reorder notifications")
            
            return True
            
    except Exception as e:
        logger.error(f"Error managing SNS subscription: {str(e)}")
        return False

@app.route('/user_account', methods=['GET', 'POST'])
def user_account():
    # Check if user has a valid session
    if 'user' not in session:
        return redirect(PRC_LOGIN + "/login")
    
    if request.method == 'POST':
        # Handle form submission
        email = request.form.get('email', '')
        building = request.form.get('building', '')
        lab_room = request.form.get('lab_room', '')
        reorder_notification = request.form.get('reorder_notification', 'off')
        
        # Update user preferences in the backend
        try:
            # Get current user info to preserve role and other fields
            user_info_request = {
                "username": session['user']
            }
            user_info_response = api_client.post(f"{PRC_BACKEND}/backend/get_user_info", json=user_info_request)
            
            if user_info_response.status_code == 200:
                user_info = user_info_response.json()
                if user_info.get('success'):
                    # Update email in the users table
                    user_data = {
                        "username": session['user'],
                        "password": "",  # We don't update the password here
                        "email": email,
                        "role": user_info.get('role', session.get('role', ''))
                    }
                    response = api_client.post(f"{PRC_BACKEND}/backend/updateuser", json=user_data)
                else:
                    raise Exception("Failed to get user information")
            else:
                raise Exception("Failed to connect to backend API")
            
            # Update preferences
            # First, get current preferences to see what needs to be updated
            pref_response = api_client.post(
                f"{PRC_BACKEND}/backend/get_user_preferences", 
                json={"username": session['user']}
            )
            
            if pref_response.status_code == 200:
                current_prefs = pref_response.json().get('preferences', {})
                
                # Update building preference if changed
                if building != current_prefs.get('building', ''):
                    building_pref = {
                        "username": session['user'],
                        "key": "building",
                        "value": building
                    }
                    api_client.post(f"{PRC_BACKEND}/backend/update_user_preference", json=building_pref)
                
                # Update lab room preference if changed
                if lab_room != current_prefs.get('lab_room', ''):
                    lab_room_pref = {
                        "username": session['user'],
                        "key": "lab_room",
                        "value": lab_room
                    }
                    api_client.post(f"{PRC_BACKEND}/backend/update_user_preference", json=lab_room_pref)
                
                # Update reorder notification preference if changed
                if reorder_notification != current_prefs.get('reorder_notification', 'off'):
                    reorder_pref = {
                        "username": session['user'],
                        "key": "reorder_notification",
                        "value": reorder_notification
                    }
                    api_client.post(f"{PRC_BACKEND}/backend/update_user_preference", json=reorder_pref)
                    
                    # Manage SNS subscription
                    manage_sns_subscription(email, reorder_notification)
                
                # Update session with new preferences
                session['pref_building'] = building
                session['pref_lab_room'] = lab_room
                session['reorder_notification'] = reorder_notification
                
                return redirect('/')
            else:
                # Get shared header and navigation
                username = session.get('user', '')
                role = session.get('role', '')
                header_html = get_shared_header(username, True)
                navigation_html = get_shared_navigation(role, 'home')
                
                return render_template('user_account.html',
                                      username=username,
                                      email=email,
                                      building=building,
                                      lab_room=lab_room,
                                      reorder_notification=reorder_notification,
                                      error="Failed to update preferences",
                                      static_url=PRC_STATIC + '/static',
                                      backend_api_url=PRC_BACKEND_BRO,
                                      header_html=header_html,
                                      navigation_html=navigation_html)
        except Exception as e:
            # Get shared header and navigation
            username = session.get('user', '')
            role = session.get('role', '')
            header_html = get_shared_header(username, True)
            navigation_html = get_shared_navigation(role, 'home')
            
            return render_template('user_account.html',
                                  username=username,
                                  email=email,
                                  building=building,
                                  lab_room=lab_room,
                                  error=str(e),
                                  static_url=PRC_STATIC + '/static',
                                  backend_api_url=PRC_BACKEND_BRO,
                                  header_html=header_html,
                                  navigation_html=navigation_html)
    
    # GET request - display the form
    try:
        # Get user email from backend
        email = ""
        try:
            # Get user data from backend using the new endpoint
            user_info_request = {
                "username": session['user']
            }
            response = api_client.post(f"{PRC_BACKEND}/backend/get_user_info", json=user_info_request)
            if response.status_code == 200:
                user_info = response.json()
                if user_info.get('success'):
                    email = user_info.get('email', '')
        except Exception as e:
            logger.error(f"Error fetching user email: {str(e)}")
        
        # Get user preferences from backend
        user_building = ''
        user_lab_room = ''
        reorder_notification = 'off'  # Default to off
        
        try:
            pref_response = api_client.post(
                f"{PRC_BACKEND}/backend/get_user_preferences", 
                json={"username": session['user']}
            )
            
            if pref_response.status_code == 200:
                prefs = pref_response.json().get('preferences', {})
                user_building = prefs.get('building', '')
                user_lab_room = prefs.get('lab_room', '')
                reorder_notification = prefs.get('reorder_notification', 'off')
                
                # Update session with preferences
                session['pref_building'] = user_building
                session['pref_lab_room'] = user_lab_room
                session['reorder_notification'] = reorder_notification
        except Exception as e:
            logger.error(f"Error fetching user preferences: {str(e)}")
            # Fall back to session values if API call fails
            user_building = session.get('pref_building', '')
            user_lab_room = session.get('pref_lab_room', '')
            reorder_notification = session.get('reorder_notification', 'off')
        
        # Get list of buildings for dropdown
        buildings_response = api_client.get(f"{PRC_BACKEND}/backend/buildings")
        buildings = []
        if buildings_response.status_code == 200:
            buildings = buildings_response.json().get('buildings', [])
        
        # Get list of lab rooms for dropdown based on selected building
        lab_rooms = []
        if user_building:
            lab_rooms_response = api_client.get(f"{PRC_BACKEND}/backend/lab_rooms/{user_building}")
            if lab_rooms_response.status_code == 200:
                lab_rooms = lab_rooms_response.json().get('lab_rooms', [])
        
        # Get shared header and navigation
        username = session.get('user', '')
        role = session.get('role', '')
        header_html = get_shared_header(username, True)
        navigation_html = get_shared_navigation(role, 'home')
        
        # Get API key for frontend requests
        api_key = api_client.get_api_key()

        return render_template('user_account.html',
                              username=username,
                              email=email,
                              building=user_building,
                              lab_room=user_lab_room,
                              reorder_notification=reorder_notification,
                              buildings=buildings,
                              lab_rooms=lab_rooms,
                              static_url=PRC_STATIC + '/static',
                              backend_api_url=PRC_BACKEND_BRO,
                              api_key=api_key,
                              header_html=header_html,
                              navigation_html=navigation_html)
    except Exception as e:
        # Get shared header and navigation
        username = session.get('user', '')
        role = session.get('role', '')
        header_html = get_shared_header(username, True)
        navigation_html = get_shared_navigation(role, 'home')
        
        return render_template('user_account.html',
                              username=username,
                              error=str(e),
                              static_url=PRC_STATIC + '/static',
                              backend_api_url=PRC_BACKEND_BRO,
                              header_html=header_html,
                              navigation_html=navigation_html)

@app.route('/set_password_reset', methods=['POST'])
def proxy_password_reset():
    """Proxy endpoint for password reset to avoid CORS issues"""
    if 'user' not in session:
        return jsonify({"success": False, "message": "Not authenticated"}), 401
    
    try:
        username = session.get('user', '')
        # Call backend API using server-side request
        # Using our api_client which automatically includes the API key in the headers
        # This ensures API key security is maintained in production/ECS environment
        response = api_client.post(
            f"{PRC_BACKEND}/backend/set_password_reset", 
            json={"username": username}
        )
        
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({"success": False, "message": f"Backend error: {response.status_code}"}), response.status_code
    
    except Exception as e:
        logger.error(f"Error in password reset proxy: {str(e)}")
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
