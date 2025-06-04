import logging
from fastapi import APIRouter, Depends, HTTPException
from ..database import get_db_connection
from ..models.chemical import (
    ChemSearchRequest,
    ChemSearchResponse,
    ReorderNotifResponse,
    InventoryUpdateRequest,
    InventoryUpdateResponse,
    ChemicalDetailsResponse
)
from ..services.chemical import search_chemicals, get_reorder_notifications, update_inventory_quantity, get_chemical_by_id

logger = logging.getLogger(__name__)
router = APIRouter(tags=["chemicals"])

@router.post("/backend/chemsearch", response_model=ChemSearchResponse)
def search_chemical_inventory(request: ChemSearchRequest):
    """Search chemicals endpoint"""
    try:
        conn = get_db_connection()
        result = search_chemicals(
            conn, 
            request.name, 
            request.building_name, 
            request.lab_room_number, 
            request.locker_number,
            request.hazard_classification
        )
        conn.close()
        return result
    except Exception as e:
        logger.error(f"Error searching chemicals: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error searching chemicals: {str(e)}")

@router.get("/backend/reorder_notif", response_model=ReorderNotifResponse)
def get_reordering_notifications():
    """Get users who should be notified about chemicals that need reordering"""
    try:
        conn = get_db_connection()
        result = get_reorder_notifications(conn)
        conn.close()
        return result
    except Exception as e:
        logger.error(f"Error getting reorder notifications: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting reorder notifications: {str(e)}")

@router.get("/backend/chemical/{inventory_id}", response_model=ChemicalDetailsResponse)
def get_chemical(inventory_id: int):
    """Get a specific chemical by its inventory ID"""
    try:
        logger.info(f"Getting chemical details for ID: {inventory_id}")
        conn = get_db_connection()
        result = get_chemical_by_id(conn, inventory_id)
        conn.close()
        
        if not result["success"]:
            logger.warning(f"Chemical not found: {inventory_id}")
            raise HTTPException(status_code=404, detail=f"Chemical with ID {inventory_id} not found")
            
        return result
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error getting chemical details: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving chemical details: {str(e)}")

@router.post("/backend/update_inventory", response_model=InventoryUpdateResponse)
def update_inventory(request: InventoryUpdateRequest):
    """Update inventory quantity endpoint"""
    conn = None
    try:
        # Log the incoming request
        logger.info(f"Processing inventory update: id={request.inventory_id}, qty={request.quantity}, action={request.action}")
        
        # Get database connection
        try:
            conn = get_db_connection()
        except Exception as conn_error:
            logger.error(f"Failed to connect to database: {str(conn_error)}")
            raise HTTPException(
                status_code=503, 
                detail=f"Database connection failed: {str(conn_error)}"
            )
        
        # Call service to update inventory
        try:
            result = update_inventory_quantity(
                conn,
                request.inventory_id,
                request.quantity,
                request.action
            )
            logger.info(f"Inventory update result: {result}")
        except ValueError as val_error:
            # Handle validation errors
            logger.error(f"Validation error: {str(val_error)}")
            if conn:
                conn.close()
            raise HTTPException(status_code=400, detail=str(val_error))
        except Exception as service_error:
            # Handle other service errors
            logger.error(f"Service error in update_inventory_quantity: {str(service_error)}")
            if conn:
                conn.close()
            raise HTTPException(
                status_code=500, 
                detail=f"Error processing inventory update: {str(service_error)}"
            )
        
        # Close connection
        if conn:
            conn.close()
        
        # If operation failed, return 400 Bad Request
        if not result["success"]:
            logger.warning(f"Inventory update failed: {result['message']}")
            raise HTTPException(status_code=400, detail=result["message"])
            
        return result
    except HTTPException:
        # Re-raise HTTP exceptions to preserve status code
        raise
    except Exception as e:
        logger.error(f"Unhandled error updating inventory: {str(e)}", exc_info=True)
        if conn:
            try:
                conn.close()
            except:
                pass
        raise HTTPException(
            status_code=500, 
            detail=f"An unexpected error occurred while updating inventory"
        )
