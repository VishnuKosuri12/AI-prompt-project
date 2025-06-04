import logging
import psycopg2
import psycopg2.extras

logger = logging.getLogger(__name__)

def update_inventory_quantity(conn, inventory_id, quantity, action):
    """
    Update inventory quantity based on action (add or remove)
    
    Args:
        conn: Database connection
        inventory_id: ID of the inventory record to update
        quantity: Quantity to add or remove
        action: 'add' or 'remove'
    
    Returns:
        Dict containing success status, new quantity, and message
    """
    cursor = None
    try:
        # Log the incoming parameters
        logger.info(f"Updating inventory: id={inventory_id}, qty={quantity}, action={action}")
        
        cursor = conn.cursor()
        
        # First get current quantity
        query = "SELECT quantity, reorder_quantity FROM inventory WHERE id = %s"
        logger.debug(f"Executing query: {query} with params: {(inventory_id,)}")
        cursor.execute(query, (inventory_id,))
        
        result = cursor.fetchone()
        if not result:
            logger.error(f"Inventory record {inventory_id} not found")
            return {
                "success": False,
                "new_quantity": 0,
                "message": f"Inventory record {inventory_id} not found"
            }
        
        current_quantity, reorder_quantity = result
        logger.info(f"Current quantity: {current_quantity}, Reorder quantity: {reorder_quantity}")
        
        # Convert values to compatible types (decimal.Decimal)
        from decimal import Decimal
        try:
            current_quantity = Decimal(str(current_quantity))
            quantity_to_update = Decimal(str(quantity))
            logger.debug(f"Converted quantities: current={current_quantity}, update={quantity_to_update}")
        except Exception as dec_err:
            logger.error(f"Error converting quantity values: {str(dec_err)}")
            raise ValueError(f"Invalid quantity values: {str(dec_err)}")
        
        # Calculate new quantity based on action
        if action == "add":
            new_quantity = current_quantity + quantity_to_update
            logger.info(f"Adding {quantity_to_update} to {current_quantity}, new quantity: {new_quantity}")
        elif action == "remove":
            new_quantity = current_quantity - quantity_to_update
            logger.info(f"Removing {quantity_to_update} from {current_quantity}, new quantity: {new_quantity}")
            # Prevent negative inventory
            if new_quantity < 0:
                logger.warning(f"Attempted to remove {quantity_to_update} from {current_quantity}, would result in negative inventory")
                return {
                    "success": False,
                    "new_quantity": float(current_quantity),
                    "message": f"Cannot remove more than available quantity ({current_quantity})"
                }
        else:
            logger.error(f"Invalid action provided: {action}")
            return {
                "success": False,
                "new_quantity": float(current_quantity),
                "message": f"Invalid action: {action}. Must be 'add' or 'remove'"
            }
        
        # Update the inventory record
        update_query = "UPDATE inventory SET quantity = %s WHERE id = %s"
        logger.debug(f"Executing update: {update_query} with params: ({new_quantity}, {inventory_id})")
        try:
            cursor.execute(update_query, (new_quantity, inventory_id))
            rows_affected = cursor.rowcount
            logger.info(f"Update affected {rows_affected} rows")
            
            if rows_affected == 0:
                logger.warning(f"Update did not change any rows for inventory_id={inventory_id}")
        except Exception as sql_err:
            logger.error(f"SQL error during inventory update: {str(sql_err)}")
            raise sql_err
        
        # Commit the transaction
        logger.debug("Committing transaction")
        conn.commit()
        
        # Close the cursor
        if cursor and not cursor.closed:
            cursor.close()
        
        # Create notification message about reordering if needed
        reorder_message = ""
        if new_quantity < reorder_quantity:
            reorder_message = " Quantity is below reorder level."
            logger.info(f"Inventory below reorder level: current={new_quantity}, reorder={reorder_quantity}")
        
        result = {
            "success": True,
            "new_quantity": float(new_quantity),  # Convert Decimal to float for JSON serialization
            "message": f"Inventory updated successfully.{reorder_message}"
        }
        logger.info(f"Inventory update successful: {result}")
        return result
    
    except Exception as e:
        logger.error(f"Error updating inventory: {str(e)}", exc_info=True)
        if cursor and not cursor.closed:
            cursor.close()
        try:
            conn.rollback()
            logger.info("Transaction rolled back")
        except Exception as rollback_err:
            logger.error(f"Error during rollback: {str(rollback_err)}")
        
        # Re-raise the exception with more context
        raise Exception(f"Inventory update failed: {str(e)}")

def search_chemicals(conn, name=None, building_name=None, lab_room_number=None, locker_number=None, hazard_classification=None):
    """Search chemicals based on provided criteria"""
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        # Build the query
        query = """
            SELECT 
                i.id,
                c.name,
                c.unit_of_measure,
                i.quantity,
                i.reorder_quantity,
                l.building_name,
                l.lab_room_number,
                l.locker_number,
                c.cas_number,
                c.chemical_formula,
                c.signal_word,
                c.physical_state,
                c.hazard_classification,
                c.chemical_description,
                c.molecular_weight,
                c.sds_link
            FROM 
                inventory i
                JOIN chemicals c ON i.chemical_id = c.id
                JOIN locations l ON i.location_id = l.location_id
            WHERE 1=1
        """
        
        params = []
        
        # Add filters based on request parameters
        if name:
            query += " AND c.name ILIKE %s"
            params.append(f"%{name}%")
        
        if building_name:
            query += " AND l.building_name = %s"
            params.append(building_name)
        
        if lab_room_number is not None:
            query += " AND l.lab_room_number = %s"
            params.append(lab_room_number)
        
        if locker_number is not None:
            query += " AND l.locker_number = %s"
            params.append(locker_number)
        
        if hazard_classification:
            query += " AND c.hazard_classification ILIKE %s"
            params.append(f"%{hazard_classification}%")

        query += " ORDER BY c.name"
        
        # Execute the query
        cursor.execute(query, params)
        
        # Process the results
        chemicals = []
        for row in cursor:
            chemicals.append({
                "id": row['id'],
                "name": row['name'],
                "unit_of_measure": row['unit_of_measure'],
                "quantity": float(row['quantity']),
                "reorder_quantity": float(row['reorder_quantity']),
                "building_name": row['building_name'],
                "lab_room_number": row['lab_room_number'],
                "locker_number": row['locker_number'],
                "cas_number": row['cas_number'],
                "chemical_formula": row['chemical_formula'],
                "signal_word": row['signal_word'],
                "physical_state": row['physical_state'],
                "hazard_classification": row['hazard_classification'],
                "chemical_description": row['chemical_description'],
                "molecular_weight": row['molecular_weight'],
                "sds_link": row['sds_link']
            })
        
        cursor.close()
        return {
            "success": True,
            "results": chemicals,
            "message": f"Found {len(chemicals)} chemicals matching the criteria"
        }
    
    except Exception as e:
        logger.error(f"Error searching chemicals: {str(e)}")
        if 'cursor' in locals() and not cursor.closed:
            cursor.close()
        raise e

def get_chemical_by_id(conn, inventory_id):
    """Get a specific chemical by its inventory ID"""
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        # Build the query
        query = """
            SELECT 
                i.id,
                c.name,
                c.unit_of_measure,
                i.quantity,
                i.reorder_quantity,
                l.building_name,
                l.lab_room_number,
                l.locker_number,
                c.cas_number,
                c.chemical_formula,
                c.signal_word,
                c.physical_state,
                c.hazard_classification,
                c.chemical_description,
                c.molecular_weight,
                c.sds_link
            FROM 
                inventory i
                JOIN chemicals c ON i.chemical_id = c.id
                JOIN locations l ON i.location_id = l.location_id
            WHERE 
                i.id = %s
        """
        
        # Execute the query
        cursor.execute(query, (inventory_id,))
        
        # Process the result
        row = cursor.fetchone()
        if not row:
            cursor.close()
            return {
                "success": False,
                "chemical": None,
                "message": f"Chemical with inventory ID {inventory_id} not found"
            }
        
        chemical = {
            "id": row['id'],
            "name": row['name'],
            "unit_of_measure": row['unit_of_measure'],
            "quantity": float(row['quantity']),
            "reorder_quantity": float(row['reorder_quantity']),
            "building_name": row['building_name'],
            "lab_room_number": row['lab_room_number'],
            "locker_number": row['locker_number'],
            "cas_number": row['cas_number'],
            "chemical_formula": row['chemical_formula'],
            "signal_word": row['signal_word'],
            "physical_state": row['physical_state'],
            "hazard_classification": row['hazard_classification'],
            "chemical_description": row['chemical_description'],
            "molecular_weight": row['molecular_weight'],
            "sds_link": row['sds_link']
        }
        
        cursor.close()
        return {
            "success": True,
            "chemical": chemical,
            "message": "Chemical found"
        }
    
    except Exception as e:
        logger.error(f"Error getting chemical by ID: {str(e)}")
        if 'cursor' in locals() and not cursor.closed:
            cursor.close()
        raise e

def get_reorder_notifications(conn):
    """Get users who should be notified about chemicals that need reordering"""
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        # Find all chemicals where quantity is below reorder_quantity
        query = """
            WITH low_inventory AS (
                SELECT 
                    i.id,
                    c.name,
                    c.unit_of_measure,
                    i.quantity,
                    i.reorder_quantity,
                    l.building_name,
                    l.lab_room_number,
                    l.location_id
                FROM 
                    inventory i
                    JOIN chemicals c ON i.chemical_id = c.id
                    JOIN locations l ON i.location_id = l.location_id
                WHERE 
                    i.quantity < i.reorder_quantity
            ),
            users_with_prefs AS (
                SELECT 
                    u.user_name,
                    u.email_address,
                    up_building.preference_value as building,
                    up_lab.preference_value as lab_room,
                    up_notif.preference_value as notification_pref
                FROM 
                    users u
                    LEFT JOIN user_preferences up_building ON u.user_name = up_building.user_name AND up_building.preference_key = 'building'
                    LEFT JOIN user_preferences up_lab ON u.user_name = up_lab.user_name AND up_lab.preference_key = 'lab_room'
                    LEFT JOIN user_preferences up_notif ON u.user_name = up_notif.user_name AND up_notif.preference_key = 'reorder_notification'
                WHERE
                    up_notif.preference_value = 'on'
            )
            SELECT 
                u.user_name,
                u.email_address,
                li.id,
                li.name,
                li.unit_of_measure,
                li.quantity,
                li.reorder_quantity,
                li.building_name,
                li.lab_room_number
            FROM 
                users_with_prefs u
                JOIN low_inventory li ON (
                    (u.building = li.building_name OR u.building IS NULL OR u.building = '') 
                    AND 
                    (CAST(u.lab_room AS INTEGER) = li.lab_room_number OR u.lab_room IS NULL OR u.lab_room = '')
                )
            ORDER BY 
                u.user_name, li.name
        """
        
        cursor.execute(query)
        
        # Organize results by user
        user_chemicals = {}
        for row in cursor:
            username = row['user_name']
            
            if username not in user_chemicals:
                user_chemicals[username] = {
                    "username": username,
                    "email": row['email_address'],
                    "chemicals": []
                }
            
            user_chemicals[username]["chemicals"].append({
                "id": row['id'],
                "name": row['name'],
                "unit_of_measure": row['unit_of_measure'],
                "quantity": float(row['quantity']),
                "reorder_quantity": float(row['reorder_quantity']),
                "building_name": row['building_name'],
                "lab_room_number": row['lab_room_number']
            })
        
        # Convert to list for response
        users = list(user_chemicals.values())
        
        cursor.close()
        return {
            "success": True,
            "users": users,
            "message": f"Found {len(users)} users to notify"
        }
    
    except Exception as e:
        logger.error(f"Error getting reorder notifications: {str(e)}")
        if 'cursor' in locals() and not cursor.closed:
            cursor.close()
        raise e
