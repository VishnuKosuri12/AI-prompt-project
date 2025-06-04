import os
import time
from flask import Flask, render_template, request, redirect, url_for, jsonify, send_from_directory
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create Flask WSGI application
app = Flask(__name__)

# Secret key for session encryption - in production, this would be loaded from environment variables
app.secret_key = os.environ.get('SECRET_KEY', 'dev_secret_key')

BASE_URL = os.environ.get('BASE_URL')
if "chemtrack" in BASE_URL:
    PRC_BACKEND = 'https://' + BASE_URL
    PRC_MAIN = ''
    PRC_SEARCH = ''
    PRC_STATIC = ''
    PRC_ADMIN = ''
    PRC_RECIPES = ''
    PRC_REPORTS = ''
else:
    PRC_BACKEND = 'http://localhost:8000'
    PRC_MAIN = 'http://localhost:8003'
    PRC_SEARCH = 'http://localhost:8004'
    PRC_STATIC = 'http://localhost:8002'
    PRC_ADMIN = 'http://localhost:8006'
    PRC_RECIPES = 'http://localhost:8007'
    PRC_REPORTS = 'http://localhost:8008'
    
    logger.info(f'Backend API URL: {PRC_BACKEND}')
    logger.info(f'Main URL: {PRC_MAIN}')
    logger.info(f'Admin URL: {PRC_ADMIN}')
    logger.info(f'Recipes URL: {PRC_RECIPES}')

# Middleware to track request metrics
@app.before_request
def before_request():
    request.start_time = time.time()

@app.after_request
def after_request(response):
    request_latency = time.time() - request.start_time
    return response


@app.route('/shared-templates/header')
def header():
    """Render the header template"""
    logger.info("/shared-templates/header")
    username = request.args.get('username', '')
    user_account_enabled = request.args.get('user_account_enabled', 'false').lower() == 'true'
    
    return render_template('shared/header.html', 
                          username=username,
                          static_url=PRC_STATIC + "/static",
                          user_account_enabled=user_account_enabled,
                          main_url=PRC_MAIN)

@app.route('/shared-templates/navigation')
def navigation():
    """Render the navigation template"""
    logger.info("/shared-templates/navigation")
    role = request.args.get('role', '')
    active_page = request.args.get('active_page', '')
    current_path = request.args.get('current_path', '')
    
    logger.info(f'>>> Admin URL: {PRC_ADMIN}')
    return render_template('shared/navigation.html', 
                          role=role,
                          active_page=active_page,
                          current_path=current_path,
                          main_url=PRC_MAIN,
                          search_url=PRC_SEARCH + '/search',
                          recipes_url=PRC_RECIPES,
                          reports_url=PRC_REPORTS,
                          admin_url=PRC_ADMIN)

@app.route('/shared-templates/base_layout')
def base_layout():
    """Render the base layout template"""
    return render_template('shared/base_layout.html')

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy"})

@app.route('/test')
def test():
    """Test endpoint to verify the service is running"""
    return """
    <html>
        <head>
            <title>Shared Templates Test</title>
        </head>
        <body>
            <h1>Shared Templates Service is Running</h1>
            <p>This is a test page to verify that the shared-templates service is running correctly.</p>
            <h2>Available Endpoints:</h2>
            <ul>
                <li><a href="/shared-templates/header?username=testuser&static_url=http://localhost:8002&user_account_enabled=true">/shared-templates/header</a></li>
                <li><a href="/shared-templates/navigation?role=user&active_page=home&search_url=/search">/shared-templates/navigation</a></li>
                <li><a href="/shared-templates/base_layout">/shared-templates/base_layout</a></li>
                <li><a href="/health">/health</a></li>
            </ul>
        </body>
    </html>
    """

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
