import logging
from datetime import datetime, timedelta
import psycopg2
from ..utils import hash_password
from ..services.preference import get_user_preferences

logger = logging.getLogger(__name__)

def login_user(conn, username: str, password: str):
    """Handle user login logic"""
    try:
        cursor = conn.cursor()
        
        # Hash the password
        hashed_password = hash_password(password)
        
        # Query the database
        query = """
            SELECT user_name, role_name, pswd_reset, last_reset
            FROM users 
            WHERE user_name = %s AND password = %s
        """
        
        cursor.execute(query, (username, hashed_password))
        user = cursor.fetchone()
        
        if user:
            logger.info(f'Login success: {username}')
            
            # Get user preferences
            preferences = get_user_preferences(conn, username)
            
            # Add password reset flag to preferences
            preferences['pswd_reset'] = user[2]
            
            # Check if password is expired (older than 90 days)
            last_reset = user[3]
            if last_reset and (datetime.now() - last_reset) > timedelta(days=90):
                logger.info(f'Password expired for user: {username}')
                # Set password reset flag to 'Y'
                update_query = """
                    UPDATE users
                    SET pswd_reset = 'Y'
                    WHERE user_name = %s
                """
                cursor.execute(update_query, (username,))
                conn.commit()
                preferences['pswd_reset'] = 'Y'
            
            cursor.close()
            return {"success": True, "role": user[1], "preferences": preferences}
        else:
            logger.warning(f'Login failure: {username}')
            cursor.close()
            return {"success": False, "message": "Invalid username or password"}
    
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        if not cursor.closed:
            cursor.close()
        raise e

def update_password(conn, username: str, old_password: str, new_password: str):
    """Update user password"""
    try:
        cursor = conn.cursor()
        
        # Check if user exists with old password
        query = """
            SELECT user_name
            FROM users 
            WHERE user_name = %s AND password = %s
        """       
        cursor.execute(query, (username, hash_password(old_password)))
        if not cursor.fetchone():
            logger.error('Old password does not match')
            cursor.close()
            return {"success": False, "message": "Old password does not match"}
        
        # Update password
        update_query = """
            UPDATE users 
            SET password = %s, pswd_reset = 'N', last_reset = CURRENT_TIMESTAMP
            WHERE user_name = %s
        """
        cursor.execute(update_query, [hash_password(new_password), username])
        
        conn.commit()
        cursor.close()
        return {"success": True, "message": "User password updated successfully"}
    
    except Exception as e:
        logger.error(f"Password update error: {str(e)}")
        conn.rollback()
        if not cursor.closed:
            cursor.close()
        raise e

def set_password_reset(conn, username: str):
    """Set the password reset flag for a user"""
    try:
        logger.info(f"Setting password reset flag for user: {username}")
        cursor = conn.cursor()
        
        # Check if the user exists
        check_query = "SELECT user_name FROM users WHERE user_name = %s"
        cursor.execute(check_query, (username,))
        if not cursor.fetchone():
            logger.error(f"User not found: {username}")
            cursor.close()
            return {"success": False, "message": "User does not exist"}
        
        # Force set the value to 'Y'
        new_value = 'Y'
        
        # Update the user's pswd_reset flag
        update_query = """
            UPDATE users
            SET pswd_reset = %s
            WHERE user_name = %s
        """
        cursor.execute(update_query, (new_value, username))
        conn.commit()
        
        logger.info(f"Password reset flag set to 'Y' for user: {username}")
        cursor.close()
        return {"success": True, "message": f"Password reset flag set for user {username}"}
    
    except Exception as e:
        logger.error(f"Error setting password reset flag: {str(e)}")
        conn.rollback()
        if not cursor.closed:
            cursor.close()
        raise e
