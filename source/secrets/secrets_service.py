import os
import logging
import boto3
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from botocore.exceptions import ClientError
import uvicorn
from fastapi.security import APIKeyHeader
import ipaddress
from typing import List, Optional

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Environment variables
HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", "8099"))
API_KEY_NAME = os.environ.get("API_KEY_PARAM_NAME", "chemtrack-api-key")
LOCAL_DEV = os.environ.get("LOCAL_DEV", "false").lower() == "true"

# Initialize FastAPI
app = FastAPI(title="ChemTrack Secrets API", 
              description="API for retrieving API keys securely", 
              docs_url=None,  # Disable docs to reduce exposure
              redoc_url=None) # Disable redoc to reduce exposure

# Set up CORS - strictly limit this in production
if LOCAL_DEV:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["GET"],
        allow_headers=["*"],
    )
else:
    # In production, only allow other containers
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"], # Will be set by container IPs/hostnames
        allow_credentials=True,
        allow_methods=["GET"],
        allow_headers=["*"],
    )

# API Key in memory cache
_api_key = None

# Trusted CIDR blocks for internal services
# In a real environment, these would be your VPC CIDR blocks or container subnets
TRUSTED_CIDR_BLOCKS = [
    "10.0.0.0/8",    # Private IP range
    "172.16.0.0/12", # Private IP range
    "192.168.0.0/16", # Private IP range
    "127.0.0.1/32"
]

# For local development
if LOCAL_DEV:
    TRUSTED_CIDR_BLOCKS.append("127.0.0.1/32")  # Allow localhost

def is_trusted_ip(client_ip: str) -> bool:
    """Check if client IP is in trusted CIDR blocks"""
    logger.info(f"Test trusted ip: {client_ip}")
    try:
        client_ip_obj = ipaddress.ip_address(client_ip)
        return any(
            client_ip_obj in ipaddress.ip_network(cidr)
            for cidr in TRUSTED_CIDR_BLOCKS
        )
    except ValueError:
        logger.warning(f"Invalid ip address: {client_ip}")
        return False

def get_api_key_from_parameter_store() -> Optional[str]:
    """Retrieve API key from AWS Parameter Store"""
    global _api_key
    
    logger.info("get api key request")
    # Return from cache if available
    if _api_key is not None:
        return _api_key
    
    if LOCAL_DEV:
        logger.info("Running in local development mode. Using dummy API key.")
        _api_key = "local-development-key"
        return _api_key
    
    try:
        region = os.environ.get('AWS_REGION', 'us-east-1')
        ssm_client = boto3.client('ssm', region_name=region)
        
        response = ssm_client.get_parameter(
            Name=API_KEY_NAME,
            WithDecryption=True
        )
        
        _api_key = response.get('Parameter', {}).get('Value')
        logger.info("Successfully retrieved API key from Parameter Store")
        return _api_key
    except ClientError as e:
        logger.error(f"Error retrieving API key from Parameter Store: {e}")
        return None

@app.middleware("http")
async def check_client_ip(request: Request, call_next):
    """Middleware to check if client IP is trusted"""
    # Allow health check endpoint for ALB health checks
    if request.url.path == "/health":
        return await call_next(request)
        
    client_ip = request.client.host
    logging.info(f"Client ip address: {client_ip}")
    
    # Always allow in local dev mode
    if LOCAL_DEV:
        return await call_next(request)
    
    if not is_trusted_ip(client_ip):
        logger.warning(f"Unauthorized access attempt from IP: {client_ip}")
        raise HTTPException(status_code=403, detail="Access denied")
    
    return await call_next(request)

@app.get("/secrets/api-key")
async def get_api_key():
    """Get API key - only accessible from trusted IPs"""
    key = get_api_key_from_parameter_store()
    if not key:
        raise HTTPException(status_code=500, detail="Failed to retrieve API key")
    return {"api_key": key}

@app.get("/health")
async def health_check():
    """Health check endpoint - returns immediately for ALB health checks"""
    # Don't perform any operations that could cause delays
    # No Parameter Store calls, no database checks, just return healthy
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("secrets_service:app", host=HOST, port=PORT, reload=LOCAL_DEV)
