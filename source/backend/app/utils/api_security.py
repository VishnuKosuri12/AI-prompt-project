import os
from typing import Optional, Callable
import logging
from fastapi import Request, HTTPException, status
import boto3
from botocore.exceptions import ClientError
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)

class ApiKeyMiddleware(BaseHTTPMiddleware):
    """Middleware for API key validation"""
    
    def __init__(self, app, api_key: Optional[str] = None):
        super().__init__(app)
        self._api_key = api_key
        self._is_enabled = False
        
        # Determine if we should enable API key security
        if os.environ.get("LOCAL_DEV") == "true":
            logger.info("API key security disabled in local development mode")
            self._is_enabled = False
        elif os.environ.get("API_KEY_SECURITY") == "enabled":
            # In ECS mode, the API key should be fetched from Parameter Store
            if not api_key:
                self._api_key = self._get_api_key_from_parameter_store()
                
            if self._api_key:
                logger.info("API key security enabled")
                self._is_enabled = True
            else:
                logger.warning("API key not found, security disabled")
                self._is_enabled = False
        else:
            logger.info("API key security not explicitly enabled")
            self._is_enabled = False
    
    def _get_api_key_from_parameter_store(self) -> Optional[str]:
        """Fetch API key from AWS Parameter Store"""
        try:
            region = os.environ.get("AWS_REGION", "us-east-1")
            ssm_client = boto3.client('ssm', region_name=region)
            
            response = ssm_client.get_parameter(
                Name="chemtrack-api-key",
                WithDecryption=True
            )
            
            return response.get('Parameter', {}).get('Value')
        except ClientError as e:
            logger.error(f"Error retrieving API key from Parameter Store: {e}")
            return None
    
    async def dispatch(self, request: Request, call_next: Callable):
        """Process the request and validate API key if enabled"""
        if not self._is_enabled:
            # Skip validation in local mode or if key not configured
            return await call_next(request)
        
        # Skip validation for health check endpoint
        if request.url.path == "/health":
            return await call_next(request)
        
        # Validate API key for all other endpoints
        api_key = request.headers.get("X-API-Key")
        
        if not api_key:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Missing API key"}
            )
        
        if api_key != self._api_key:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid API key"}
            )
        
        return await call_next(request)
