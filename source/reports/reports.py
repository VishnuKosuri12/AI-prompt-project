import os
import time
import logging
import json
from flask import Flask, render_template, request, redirect, session, jsonify, Response
import requests
from api_client import get, post

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

@app.route('/reports')
def index():
    # Check if user has a valid session
    if 'user' not in session:
        return redirect('/login')
    
    # Get shared header and navigation
    username = session.get('user', '')
    role = session.get('role', '')
    header_html = get_shared_header(username, True)
    navigation_html = get_shared_navigation(role, 'reports')
    
    # Fetch available reports from the backend
    try:
        response = get(f"{PRC_BACKEND}/reports")
        if response.status_code == 200:
            reports = response.json()
        else:
            reports = []
            logger.error(f"Failed to fetch reports: {response.status_code} - {response.text}")
    except Exception as e:
        reports = []
        logger.error(f"Exception fetching reports: {str(e)}")
    
    # User has a valid session, render the reports page
    return render_template('reports.html', 
                          username=username,
                          role=role,
                          static_url=PRC_STATIC + "/static",
                          search_url=PRC_SEARCH + "/search",
                          header_html=header_html,
                          navigation_html=navigation_html,
                          reports=reports)

@app.route('/reports/run/<int:report_id>', methods=['POST'])
def run_report(report_id):
    """Run a specific report and return the results"""
    if 'user' not in session:
        return jsonify({"error": "Not authenticated"}), 401
    
    try:
        # Execute report via backend API
        response = post(f"{PRC_BACKEND}/reports/{report_id}/execute")
        
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            logger.error(f"Error running report {report_id}: {response.status_code} - {response.text}")
            return jsonify({"error": f"Failed to run report: {response.text}"}), response.status_code
    except Exception as e:
        logger.error(f"Exception running report {report_id}: {str(e)}")
        return jsonify({"error": f"Error: {str(e)}"}), 500

@app.route('/reports/export/<int:report_id>', methods=['POST'])
def export_report(report_id):
    """Export a report to HTML for Excel"""
    if 'user' not in session:
        return jsonify({"error": "Not authenticated"}), 401
    
    try:
        # Execute report via backend API
        response = post(f"{PRC_BACKEND}/reports/{report_id}/execute")
        
        if response.status_code == 200:
            report_data = response.json()
            
            # Create HTML suitable for Excel
            excel_html = """
            <html xmlns:o="urn:schemas-microsoft-com:office:office" 
                  xmlns:x="urn:schemas-microsoft-com:office:excel"
                  xmlns="http://www.w3.org/TR/REC-html40">
            <head>
                <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
                <meta name="ProgId" content="Excel.Sheet">
                <style>
                    table { border-collapse: collapse; }
                    td, th { border: 1px solid #000; }
                </style>
            </head>
            <body>
                <table>
                    <thead>
                        <tr>
            """
            
            # Add header row with column names
            for column in report_data['columns']:
                excel_html += f"<th>{column}</th>"
            
            excel_html += """
                        </tr>
                    </thead>
                    <tbody>
            """
            
            # Add data rows
            for row in report_data['rows']:
                excel_html += "<tr>"
                for cell in row:
                    excel_html += f"<td>{cell if cell is not None else ''}</td>"
                excel_html += "</tr>"
            
            excel_html += """
                    </tbody>
                </table>
            </body>
            </html>
            """
            
            return Response(
                excel_html,
                mimetype="application/vnd.ms-excel",
                headers={"Content-disposition": f"attachment; filename=report_{report_id}.xls"}
            )
        else:
            logger.error(f"Error exporting report {report_id}: {response.status_code} - {response.text}")
            return jsonify({"error": f"Failed to export report: {response.text}"}), response.status_code
    except Exception as e:
        logger.error(f"Exception exporting report {report_id}: {str(e)}")
        return jsonify({"error": f"Error: {str(e)}"}), 500

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
