import logging
import psycopg2
import psycopg2.extras
from ..utils import hash_password
from ..services.preference import get_user_preferences

logger = logging.getLogger(__name__)

def create_user(conn, username: str, password: str, email: str, role: str):
    """Create a new user in the system"""
    try:
        cursor = conn.cursor()
        
        # Check if user already exists
        check_query = "SELECT user_name FROM users WHERE user_name = %s"
        cursor.execute(check_query, (username,))
        if cursor.fetchone():
            cursor.close()
            return {"success": False, "message": "User already exists"}
        
        # Hash the password
        hashed_password = hash_password(password)
        
        # Insert the new user
        insert_query = """
            INSERT INTO users (user_name, password, email_address, role_name)
            VALUES (%s, %s, %s, %s)
        """
        
        cursor.execute(insert_query, (
            username,
            hashed_password,
            email,
            role
        ))
        
        conn.commit()
        cursor.close()
        return {"success": True, "message": "User created successfully"}
    
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        conn.rollback()
        if 'cursor' in locals() and not cursor.closed:
            cursor.close()
        raise e

def get_user_info(conn, username: str):
    """Get user information by username"""
    try:
        cursor = conn.cursor()
        
        # Check if user exists and get their information
        query = """
            SELECT user_name, email_address, role_name
            FROM users
            WHERE user_name = %s
        """
        cursor.execute(query, (username,))
        user = cursor.fetchone()
        
        cursor.close()
        if user:
            return {
                "success": True,
                "username": user[0],
                "email": user[1],
                "role": user[2]
            }
        else:
            return {
                "success": False,
                "username": "",
                "email": "",
                "role": "",
                "message": "User not found"
            }
    
    except Exception as e:
        logger.error(f"Error getting user info: {str(e)}")
        if 'cursor' in locals() and not cursor.closed:
            cursor.close()
        raise e

def update_user(conn, username: str, email: str, role: str, password: str = None):
    """Update an existing user"""
    try:
        cursor = conn.cursor()
        
        # Check if user exists
        check_query = "SELECT user_name FROM users WHERE user_name = %s"
        cursor.execute(check_query, (username,))
        if not cursor.fetchone():
            cursor.close()
            return {"success": False, "message": "User does not exist"}
        
        # Only update fields that are provided
        update_fields = []
        update_values = []
        
        # Always update email and role
        update_fields.append("email_address = %s")
        update_values.append(email)
        
        update_fields.append("role_name = %s")
        update_values.append(role)
        
        # Only update password if provided
        if password:
            hashed_password = hash_password(password)
            update_fields.append("password = %s")
            update_values.append(hashed_password)
        
        # Add username for WHERE clause
        update_values.append(username)
        
        # Build and execute the update query
        update_query = f"""
            UPDATE users 
            SET {', '.join(update_fields)}
            WHERE user_name = %s
        """
        
        cursor.execute(update_query, update_values)
        
        conn.commit()
        cursor.close()
        return {"success": True, "message": "User updated successfully"}
    
    except Exception as e:
        logger.error(f"Error updating user: {str(e)}")
        conn.rollback()
        if 'cursor' in locals() and not cursor.closed:
            cursor.close()
        raise e

def get_all_users(conn):
    """Get all users with their preferences"""
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        # Query to get all users
        query = """
            SELECT user_name, email_address, role_name
            FROM users
            ORDER BY user_name ASC
        """
        
        cursor.execute(query)
        users = []
        
        # Process the results
        for row in cursor:
            username = row['user_name']
            
            # Get user preferences
            preferences = get_user_preferences(conn, username)
            
            users.append({
                "username": username,
                "email": row['email_address'],
                "role": row['role_name'],
                "preferences": preferences
            })
        
        cursor.close()
        return {
            "success": True,
            "users": users,
            "message": f"Found {len(users)} users"
        }
    
    except Exception as e:
        logger.error(f"Error getting users: {str(e)}")
        if 'cursor' in locals() and not cursor.closed:
            cursor.close()
        raise e

def get_roles(conn):
    """Get all available roles"""
    try:
        cursor = conn.cursor()
        
        # Query to get all roles
        query = """
            SELECT DISTINCT role_name
            FROM roles
            ORDER BY role_name ASC
        """
        
        cursor.execute(query)
        roles = [row[0] for row in cursor.fetchall()]

        cursor.close()
        return {
            "success": True,
            "roles": roles,
            "message": f"Found {len(roles)} roles"
        }
    
    except Exception as e:
        logger.error(f"Error getting roles: {str(e)}")
        if 'cursor' in locals() and not cursor.closed:
            cursor.close()
        raise e

def delete_user(conn, username: str):
    """Delete a user in the system"""
    try:
        cursor = conn.cursor()
        
        # delete the user
        delete_query = """
            DELETE FROM users
            WHERE user_name = %s
        """
        
        cursor.execute(delete_query, (username,))
        conn.commit()
        cursor.close()
        return {"success": True, "message": "User deleted successfully"}
    
    except Exception as e:
        logger.error(f"Error deleting user: {str(e)}")
        conn.rollback()
        if 'cursor' in locals() and not cursor.closed:
            cursor.close()
        raise e
