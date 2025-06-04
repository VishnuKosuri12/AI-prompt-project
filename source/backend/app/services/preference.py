import logging
import psycopg2.extras

logger = logging.getLogger(__name__)

def get_user_preferences(conn, username: str, key: str = None):
    """Get user preferences from database"""
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        # Build the query
        query = """
            SELECT preference_key, preference_value
            FROM user_preferences
            WHERE user_name = %s
        """
        
        params = [username]
        
        # Add key filter if provided
        if key:
            query += " AND preference_key = %s"
            params.append(key)
        
        # Execute the query
        cursor.execute(query, params)
        
        # Process the results
        preferences = {}
        for row in cursor:
            preferences[row['preference_key']] = row['preference_value']
        
        cursor.close()
        return preferences
    
    except Exception as e:
        logger.error(f"Error in get_user_preferences: {str(e)}")
        if 'cursor' in locals() and not cursor.closed:
            cursor.close()
        raise e

def update_user_preference(conn, username: str, key: str, value: str):
    """Update or create user preference"""
    try:
        cursor = conn.cursor()
        
        # Check if the preference already exists
        check_query = """
            SELECT preference_key
            FROM user_preferences
            WHERE user_name = %s AND preference_key = %s
        """
        cursor.execute(check_query, (username, key))
        preference_exists = cursor.fetchone() is not None
        
        if preference_exists:
            # Update existing preference
            update_query = """
                UPDATE user_preferences
                SET preference_value = %s
                WHERE user_name = %s AND preference_key = %s
            """
            cursor.execute(update_query, (value, username, key))
        else:
            # Insert new preference
            insert_query = """
                INSERT INTO user_preferences (user_name, preference_key, preference_value)
                VALUES (%s, %s, %s)
            """
            cursor.execute(insert_query, (username, key, value))
        
        conn.commit()
        
        # Get updated preferences
        preferences = get_user_preferences(conn, username)
        
        cursor.close()
        return {
            "success": True,
            "preferences": preferences,
            "message": f"Preference {key} updated successfully for user {username}"
        }
    
    except Exception as e:
        logger.error(f"Error updating user preference: {str(e)}")
        conn.rollback()
        if 'cursor' in locals() and not cursor.closed:
            cursor.close()
        raise e

def delete_user_preferences(conn, username: str):
    """delete user preferences"""
    try:
        cursor = conn.cursor()
        
        delete_query = """
            DELETE FROM user_preferences 
            WHERE user_name = %s
        """
        cursor.execute(delete_query, (username,))
        conn.commit()        
        cursor.close()
        return {"success": True, "message": "Preferences deleted successfully"}
    
    except Exception as e:
        logger.error(f"Error deleting user preferences: {str(e)}")
        conn.rollback()
        if 'cursor' in locals() and not cursor.closed:
            cursor.close()
        raise e
