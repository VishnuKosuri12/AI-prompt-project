import os
import requests
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Environment variables
SECRETS_SERVICE_URL = os.environ.get('SECRETS_SERVICE_URL', 'http://localhost:8099')
LOCAL_DEV = os.environ.get("LOCAL_DEV", "false").lower() == "true"

def get_api_key() -> Optional[str]:
    """
    Get API key from secrets service
    
    Returns:
        str: API key if successful, None otherwise
    """
    # In local development mode with LOCAL_DEV=true, return a dummy key
    if LOCAL_DEV:
        logger.info("Running in local development mode. Using dummy API key.")
        return "local-development-key"
    
    try:
        response = requests.get(f"{SECRETS_SERVICE_URL}/secrets/api-key", timeout=5)
        
        if response.status_code == 200:
            return response.json().get("api_key")
        else:
            logger.error(f"Failed to retrieve API key: Status code {response.status_code}")
            return None
    except requests.RequestException as e:
        logger.error(f"Error connecting to secrets service: {e}")
        return None

def api_request(method, url, **kwargs):
    """
    Make API request with API key header
    
    Args:
        method (str): HTTP method (get, post, etc.)
        url (str): Target URL
        **kwargs: Additional arguments to pass to requests.request
    
    Returns:
        requests.Response: Response from the API
    """
    api_key = get_api_key()
    if api_key:
        headers = kwargs.get('headers', {})
        headers['X-API-Key'] = api_key
        kwargs['headers'] = headers
    
    return requests.request(method, url, **kwargs)

# Convenience methods
def get(url, **kwargs):
    return api_request('get', url, **kwargs)

def post(url, **kwargs):
    return api_request('post', url, **kwargs)
