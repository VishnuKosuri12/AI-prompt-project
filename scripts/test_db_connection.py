#!/usr/bin/env python3
import os
import sys
import json
import boto3
import psycopg2
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db_connection():
    """Get database connection from AWS Secrets Manager or local configuration"""
    try:
        # Get database URL from AWS Secrets Manager
        aws_region = os.environ.get('AWS_REGION', 'us-east-1')
        session = boto3.session.Session(region_name=aws_region)
        client = session.client(service_name='secretsmanager', region_name=aws_region)
        secret_name = "env-vars"
        
        # Get the secret value
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
        secret = json.loads(get_secret_value_response['SecretString'])
        db_url = secret.get('db_url')
        
        # Get database credentials from AWS Secrets Manager
        secret_name = "chemtrack-db-app-user"
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
        db_creds = json.loads(get_secret_value_response['SecretString'])
        username = db_creds.get('username')
        password = db_creds.get('password')

        # Parse the db_url to get host
        # Assuming db_url is in format: hostname:port or just hostname
        host = db_url.split(':')[0] if ':' in db_url else db_url
        logger.info(f"Connecting to database: {host} as {username}")
        
        # Create database connection
        conn = psycopg2.connect(
            dbname="chemtrack",
            user=username,
            password=password,
            host=host,
            port=5432
        )
        return conn
    except Exception as e:
        logger.error(f"Database connection error: {str(e)}")
        return None

def test_connection():
    """Test database connection"""
    conn = get_db_connection()
    if conn:
        logger.info("Database connection successful")
        return True
    else:
        logger.error("Database connection failed")
        return False

def check_users_table():
    """Check if users table exists and has pswd_reset column"""
    conn = get_db_connection()
    if not conn:
        return False
    
    cursor = conn.cursor()
    try:
        # Check if users table exists
        cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'users')")
        table_exists = cursor.fetchone()[0]
        if not table_exists:
            logger.error("Users table does not exist")
            return False
        
        # Check if pswd_reset column exists
        cursor.execute("SELECT EXISTS (SELECT FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'pswd_reset')")
        column_exists = cursor.fetchone()[0]
        if not column_exists:
            logger.error("pswd_reset column does not exist in users table")
            return False
        
        logger.info("Users table and pswd_reset column exist")
        
        # Check sample user data
        cursor.execute("SELECT user_name, pswd_reset FROM users LIMIT 5")
        users = cursor.fetchall()
        logger.info(f"Sample users: {users}")
        
        return True
    except Exception as e:
        logger.error(f"Error checking users table: {str(e)}")
        return False
    finally:
        cursor.close()
        conn.close()

def test_update_pswd_reset(username):
    """Test updating pswd_reset flag for a user"""
    conn = get_db_connection()
    if not conn:
        return False
    
    cursor = conn.cursor()
    try:
        # Check if user exists
        cursor.execute("SELECT user_name FROM users WHERE user_name = %s", (username,))
        user = cursor.fetchone()
        if not user:
            logger.error(f"User {username} does not exist")
            return False
        
        # Get current pswd_reset value
        cursor.execute("SELECT pswd_reset FROM users WHERE user_name = %s", (username,))
        current_value = cursor.fetchone()[0]
        logger.info(f"Current pswd_reset value for {username}: {current_value}")
        
        # Update pswd_reset value
        new_value = 'Y'
        cursor.execute("UPDATE users SET pswd_reset = %s WHERE user_name = %s", (new_value, username))
        conn.commit()
        
        # Verify update
        cursor.execute("SELECT pswd_reset FROM users WHERE user_name = %s", (username,))
        updated_value = cursor.fetchone()[0]
        logger.info(f"Updated pswd_reset value for {username}: {updated_value}")
        
        return updated_value == new_value
    except Exception as e:
        logger.error(f"Error updating pswd_reset: {str(e)}")
        return False
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    logger.info("Testing database connection...")
    if test_connection():
        logger.info("Checking users table...")
        check_users_table()
        
        # Test updating pswd_reset for a specific user if provided
        if len(sys.argv) > 1:
            username = sys.argv[1]
            logger.info(f"Testing update of pswd_reset for user {username}...")
            if test_update_pswd_reset(username):
                logger.info(f"Successfully updated pswd_reset for {username}")
            else:
                logger.error(f"Failed to update pswd_reset for {username}")
