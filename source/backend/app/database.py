import os
import json
import boto3
import psycopg2
import psycopg2.extras
import logging
from fastapi import HTTPException

logging.basicConfig(level=logging.WARN)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def get_db_connection():
    """Get database connection from AWS Secrets Manager or local configuration"""
    
    try:
        # Get database URL from AWS Secrets Manager
        aws_region = os.environ.get('AWS_REGION', 'us-east-1')
        try:
            logger.debug(f"Initializing boto3 session with region: {aws_region}")
            session = boto3.session.Session(region_name=aws_region)
            client = session.client(service_name='secretsmanager', region_name=aws_region)
        except Exception as boto_err:
            logger.error(f"Failed to initialize boto3 client: {str(boto_err)}")
            raise Exception(f"AWS client initialization failed: {str(boto_err)}")
        
        # Get database URL from secrets
        try:
            secret_name = "env-vars"
            logger.debug(f"Getting secret: {secret_name}")
            get_secret_value_response = client.get_secret_value(SecretId=secret_name)
            secret = json.loads(get_secret_value_response['SecretString'])
            db_url = secret.get('db_url')
            if not db_url:
                logger.error("db_url not found in secrets")
                raise Exception("Database URL not found in secrets")
        except Exception as secret_err:
            logger.error(f"Failed to get DB URL from secrets: {str(secret_err)}")
            raise Exception(f"Error retrieving database URL: {str(secret_err)}")
        
        # Get database credentials from AWS Secrets Manager
        try:
            secret_name = "chemtrack-db-app-user"
            logger.debug(f"Getting secret: {secret_name}")
            get_secret_value_response = client.get_secret_value(SecretId=secret_name)
            db_creds = json.loads(get_secret_value_response['SecretString'])
            username = db_creds.get('username')
            password = db_creds.get('password')
            
            if not username or not password:
                logger.error("Database credentials incomplete")
                raise Exception("Database credentials not properly configured")
        except Exception as cred_err:
            logger.error(f"Failed to get DB credentials from secrets: {str(cred_err)}")
            raise Exception(f"Error retrieving database credentials: {str(cred_err)}")

        # Parse the db_url to get host
        # Assuming db_url is in format: hostname:port or just hostname
        host = db_url.split(':')[0] if ':' in db_url else db_url
        logger.info(f"Connecting to database - Host: {host}, User: {username}")        
        
        # Create database connection
        try:
            conn = psycopg2.connect(
                dbname="chemtrack",
                user=username,
                password=password,
                host=host,
                port=5432,
                connect_timeout=10  # Set connection timeout
            )
            logger.info("Database connection established successfully")
            return conn
        except psycopg2.OperationalError as op_err:
            logger.error(f"Database operational error: {str(op_err)}")
            raise Exception(f"Could not connect to database: {str(op_err)}")
        except Exception as conn_err:
            logger.error(f"Database connection error: {str(conn_err)}")
            raise Exception(f"Database connection failed: {str(conn_err)}")
    except Exception as e:
        logger.error(f"Failed to get database connection: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Database connection error: {str(e)}")
