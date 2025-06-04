import os
import json
import time
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, Response
import logging
import api_client  # Changed from relative import to absolute import

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder=None)  # Disable static folder as it's served by nginx

# Secret key for session encryption - in production, this would be loaded from environment variables
app.secret_key = os.environ.get('SECRET_KEY', 'dev_secret_key')

# Get the application URLs
BASE_URL = os.environ.get('BASE_URL')
if "chemtrack" in BASE_URL:
    PRC_BACKEND = 'https://' + BASE_URL
    PRC_MAIN = ''
    PRC_STATIC = ''
else:
    PRC_BACKEND = 'http://ct-backend:8000'
    PRC_MAIN = 'http://localhost:8003'
    PRC_STATIC = 'http://localhost:8002'


# Ensure URLs have proper scheme for requests
logger.debug(f'base url = {BASE_URL}')
logger.debug(f'Backend API URL: {PRC_BACKEND}')
logger.debug(f'Static Content URL: {PRC_STATIC}')
logger.debug(f'Main URL: {PRC_MAIN}')

# Middleware to track request metrics
@app.before_request
def before_request():
    request.start_time = time.time()

@app.after_request
def after_request(response):
    request_latency = time.time() - request.start_time
    return response

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None

    # Check if user already has a valid session
    if 'user' in session:
        logger.debug("--- user session detected")
        return redirect('/')

    if request.method == 'POST':
        logger.debug("We have a POST event")
        username = request.form['username']
        password = request.form['password']
        try:
            # Construct the API endpoint URL
            login_endpoint = f"{PRC_BACKEND}/backend/login" 
            
            logger.debug(f"Connecting to backend API at: {login_endpoint}")
            response = api_client.post(login_endpoint, json={"username": username, "password": password}, timeout=8)
            logger.debug(f'Response status code = {response.status_code}')

            if response.status_code == 200:
                result = response.json()
                logger.debug(f"Backend API response: {result}")
                if result.get('success'):
                    # Create session for the user
                    session['user'] = username
                    session['role'] = result.get('role', '')
                    
                    # Store user preferences in session
                    preferences = result.get('preferences', {})
                    if preferences:
                        for key, value in preferences.items():
                            session[f'pref_{key}'] = value
                        logger.debug(f"Loaded user preferences: {preferences}")
                    
                    # Check if password reset is required
                    if preferences.get('pswd_reset') == 'Y':
                        logger.debug("Password reset required")
                        return redirect('/login/change_password')
                    
                    # Redirect to main page
                    return redirect('/')
                else:
                    error = "Invalid username or password"
            else:
                error = f"Authentication service unavailable (Status code: {response.status_code})"
                logger.error(f"Backend API error: {response.text}")
        except Exception as e:
            error = "Could not connect to authentication service"
            logger.error(f"Connection error: {str(e)}")
    else:
        print("display static")
    return render_template('login.html', error=error, static_url=PRC_STATIC+"/static")

@app.route('/logout')
def logout():
    # Clear the user session
    session.pop('user', None)
    session.pop('role', None)
    
    # Clear preference keys
    keys_to_remove = [key for key in session.keys() if key.startswith('pref_')]
    for key in keys_to_remove:
        session.pop(key, None)
        
    return redirect('/login')

@app.route('/')
def index():
    logger.debug("*** PUNT ***")
    # Check if user has a valid session
    if 'user' not in session:
        return redirect('/login')
    
    # Redirect to the main application page
    return redirect(PRC_MAIN)

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

@app.route('/login/change_password', methods=['GET', 'POST'])
def change_password():
    error = None
    
    # Check if user has a valid session
    if 'user' not in session:
        return redirect('/login')
    
    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        
        # Check if new passwords match
        if new_password != confirm_password:
            error = "New passwords do not match"
            return render_template('change_password.html', error=error, static_url=PRC_STATIC+"/static")
        
        try:
            # Update password
            update_endpoint = f"{PRC_BACKEND}/backend/updatepassword"
            update_response = api_client.post(
                update_endpoint,
                json={
                    "username": session['user'],
                    "old_password": current_password,
                    "new_password": new_password
                },
                timeout=8
            )
            
            if update_response.status_code == 200:
                session.clear()
                return redirect('/login')
            else:
                error = "Password update service unavailable"
        except Exception as e:
            error = "Could not connect to authentication service"
            print(f"Connection error: {str(e)}")
    
    return render_template('change_password.html', error=error, static_url=PRC_STATIC+"/static")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
