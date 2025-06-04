import logging
import psycopg2
import psycopg2.extras

logger = logging.getLogger(__name__)

def get_buildings(conn):
    """Get a list of unique building names"""
    try:
        cursor = conn.cursor()
        
        # Query to get unique building names
        query = """
            SELECT DISTINCT building_name
            FROM locations
            ORDER BY building_name ASC
        """
        
        cursor.execute(query)
        buildings = [row[0] for row in cursor.fetchall()]
        
        cursor.close()
        return {
            "success": True,
            "buildings": buildings,
            "message": f"Found {len(buildings)} buildings"
        }
    
    except Exception as e:
        logger.error(f"Error getting buildings: {str(e)}")
        if 'cursor' in locals() and not cursor.closed:
            cursor.close()
        raise e

def get_lab_rooms(conn, building_name: str):
    """Get a list of unique lab room numbers for a specific building"""
    try:
        cursor = conn.cursor()
        
        # Query to get unique lab room numbers for the specified building
        query = """
            SELECT DISTINCT lab_room_number
            FROM locations
            WHERE building_name = %s
            ORDER BY lab_room_number ASC
        """
        
        cursor.execute(query, (building_name,))
        lab_rooms = [row[0] for row in cursor.fetchall()]
        
        cursor.close()
        return {
            "success": True,
            "lab_rooms": lab_rooms,
            "message": f"Found {len(lab_rooms)} lab rooms for building {building_name}"
        }
    
    except Exception as e:
        logger.error(f"Error getting lab rooms: {str(e)}")
        if 'cursor' in locals() and not cursor.closed:
            cursor.close()
        raise e

def get_locations(conn):
    """Get all locations from database"""
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        # Query to get all locations
        query = """
            SELECT location_id, building_name, lab_room_number, locker_number
            FROM locations
            ORDER BY building_name ASC, lab_room_number ASC, locker_number ASC
        """
        
        cursor.execute(query)
        locations = []
        
        # Process the results
        for row in cursor:
            locations.append({
                "location_id": row['location_id'],
                "building_name": row['building_name'],
                "lab_room_number": row['lab_room_number'],
                "locker_number": row['locker_number']
            })
        
        cursor.close()    
        return {
            "success": True,
            "locations": locations,
            "message": f"Found {len(locations)} locations"
        }
    
    except Exception as e:
        logger.error(f"Error getting locations: {str(e)}")
        if 'cursor' in locals() and not cursor.closed:
            cursor.close()
        raise e

def create_location(conn, building_name: str, lab_room_number: int, locker_number: int):
    """Create a new location"""
    try:
        cursor = conn.cursor()
        
        # Check if location with same building, room, and locker already exists
        check_query = """
            SELECT location_id 
            FROM locations 
            WHERE building_name = %s AND lab_room_number = %s AND locker_number = %s
        """
        cursor.execute(check_query, (building_name, lab_room_number, locker_number))
        existing_location = cursor.fetchone()
        
        if existing_location:
            cursor.close()
            return {
                "success": False, 
                "message": f"Location already exists with building {building_name}, room {lab_room_number}, locker {locker_number}"
            }
        
        # Insert new location
        insert_query = """
            INSERT INTO locations (building_name, lab_room_number, locker_number)
            VALUES (%s, %s, %s)
            RETURNING location_id
        """
        cursor.execute(insert_query, (building_name, lab_room_number, locker_number))
        new_location_id = cursor.fetchone()[0]
        conn.commit()
        
        cursor.close()
        return {
            "success": True, 
            "message": "Location created successfully",
            "location_id": new_location_id
        }
    
    except Exception as e:
        logger.error(f"Error creating location: {str(e)}")
        conn.rollback()
        if 'cursor' in locals() and not cursor.closed:
            cursor.close()
        raise e

def update_location(conn, location_id: int, building_name: str, lab_room_number: int, locker_number: int):
    """Update an existing location"""
    try:
        if not location_id:
            return {
                "success": False, 
                "message": "Location ID is required for update"
            }
        
        cursor = conn.cursor()
        
        # Check if location exists
        check_query = "SELECT location_id FROM locations WHERE location_id = %s"
        cursor.execute(check_query, (location_id,))
        if not cursor.fetchone():
            cursor.close()
            return {
                "success": False, 
                "message": f"Location with ID {location_id} not found"
            }
        
        # Check if another location with same building, room, and locker exists (excluding this one)
        check_duplicate_query = """
            SELECT location_id 
            FROM locations 
            WHERE building_name = %s AND lab_room_number = %s AND locker_number = %s AND location_id != %s
        """
        cursor.execute(check_duplicate_query, (
            building_name, 
            lab_room_number,
            locker_number,
            location_id
        ))
        existing_location = cursor.fetchone()
        
        if existing_location:
            cursor.close()
            return {
                "success": False, 
                "message": f"Another location already exists with building {building_name}, room {lab_room_number}, locker {locker_number}"
            }
        
        # Update location
        update_query = """
            UPDATE locations
            SET building_name = %s, lab_room_number = %s, locker_number = %s
            WHERE location_id = %s
        """
        cursor.execute(update_query, (
            building_name, 
            lab_room_number,
            locker_number,
            location_id
        ))
        conn.commit()
        
        cursor.close()
        return {
            "success": True, 
            "message": "Location updated successfully",
            "location_id": location_id
        }
    
    except Exception as e:
        logger.error(f"Error updating location: {str(e)}")
        conn.rollback()
        if 'cursor' in locals() and not cursor.closed:
            cursor.close()
        raise e

def check_location(conn, location_id: int):
    """Check if a location has inventory associated with it"""
    try:
        cursor = conn.cursor()
        
        # Check if location exists
        check_query = "SELECT location_id FROM locations WHERE location_id = %s"
        cursor.execute(check_query, (location_id,))
        if not cursor.fetchone():
            cursor.close()
            return {
                "success": False, 
                "has_inventory": False,
                "message": f"Location with ID {location_id} not found"
            }
        
        # Check if location has inventory
        inventory_query = "SELECT COUNT(*) FROM inventory WHERE location_id = %s"
        cursor.execute(inventory_query, (location_id,))
        inventory_count = cursor.fetchone()[0]
        
        cursor.close()
        return {
            "success": True, 
            "has_inventory": inventory_count > 0,
            "message": f"Location has {inventory_count} inventory items"
        }
    
    except Exception as e:
        logger.error(f"Error checking location inventory: {str(e)}")
        if 'cursor' in locals() and not cursor.closed:
            cursor.close()
        raise e

def delete_location(conn, location_id: int):
    """Delete a location if it has no inventory"""
    try:
        cursor = conn.cursor()
        
        # Check if location exists
        check_query = "SELECT location_id FROM locations WHERE location_id = %s"
        cursor.execute(check_query, (location_id,))
        if not cursor.fetchone():
            cursor.close()
            return {
                "success": False, 
                "message": f"Location with ID {location_id} not found"
            }
        
        # Check if location has inventory
        inventory_query = "SELECT COUNT(*) FROM inventory WHERE location_id = %s"
        cursor.execute(inventory_query, (location_id,))
        inventory_count = cursor.fetchone()[0]
        
        if inventory_count > 0:
            cursor.close()
            return {
                "success": False, 
                "message": f"Cannot delete location with ID {location_id}. It has {inventory_count} inventory items."
            }
        
        # Delete location
        delete_query = "DELETE FROM locations WHERE location_id = %s"
        cursor.execute(delete_query, (location_id,))
        conn.commit()
        
        cursor.close()
        return {
            "success": True, 
            "message": f"Location with ID {location_id} deleted successfully"
        }
    
    except Exception as e:
        logger.error(f"Error deleting location: {str(e)}")
        conn.rollback()
        if 'cursor' in locals() and not cursor.closed:
            cursor.close()
        raise e
