import logging
from fastapi import APIRouter, Depends, HTTPException, Path
from ..database import get_db_connection
from ..models.location import (
    BuildingListResponse,
    LabRoomListResponse,
    LocationsListResponse,
    LocationCreateUpdateRequest,
    LocationResponse,
    LocationCheckResponse
)
from ..services.location import (
    get_buildings,
    get_lab_rooms,
    get_locations,
    create_location,
    update_location,
    check_location,
    delete_location
)

logger = logging.getLogger(__name__)
router = APIRouter(tags=["locations"])

@router.get("/backend/buildings", response_model=BuildingListResponse)
def get_all_buildings():
    """Get a list of unique building names"""
    try:
        conn = get_db_connection()
        result = get_buildings(conn)
        conn.close()
        return result
    except Exception as e:
        logger.error(f"Error getting buildings: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting buildings: {str(e)}")

@router.get("/backend/lab_rooms/{building_name}", response_model=LabRoomListResponse)
def get_lab_rooms_for_building(
    building_name: str = Path(..., description="Building name to filter lab rooms")
):
    """Get a list of unique lab room numbers for a specific building"""
    try:
        conn = get_db_connection()
        result = get_lab_rooms(conn, building_name)
        conn.close()
        return result
    except Exception as e:
        logger.error(f"Error getting lab rooms: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting lab rooms: {str(e)}")

@router.get("/backend/locations", response_model=LocationsListResponse)
def get_all_locations():
    """Get all locations endpoint"""
    try:
        conn = get_db_connection()
        result = get_locations(conn)
        conn.close()
        return result
    except Exception as e:
        logger.error(f"Error getting locations: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting locations: {str(e)}")

@router.post("/backend/createlocation", response_model=LocationResponse)
def create_new_location(request: LocationCreateUpdateRequest):
    """Create a new location"""
    try:
        conn = get_db_connection()
        result = create_location(
            conn,
            request.building_name,
            request.lab_room_number,
            request.locker_number
        )
        conn.close()
        return result
    except Exception as e:
        logger.error(f"Error creating location: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating location: {str(e)}")

@router.post("/backend/updatelocation", response_model=LocationResponse)
def update_existing_location(request: LocationCreateUpdateRequest):
    """Update an existing location"""
    try:
        if not request.location_id:
            return LocationResponse(success=False, message="Location ID is required for update")
        
        conn = get_db_connection()
        result = update_location(
            conn,
            request.location_id,
            request.building_name,
            request.lab_room_number,
            request.locker_number
        )
        conn.close()
        return result
    except Exception as e:
        logger.error(f"Error updating location: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating location: {str(e)}")

@router.get("/backend/checklocation/{location_id}", response_model=LocationCheckResponse)
def check_location_inventory(location_id: int):
    """Check if a location has inventory associated with it"""
    try:
        conn = get_db_connection()
        result = check_location(conn, location_id)
        conn.close()
        return result
    except Exception as e:
        logger.error(f"Error checking location inventory: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error checking location inventory: {str(e)}")

@router.delete("/backend/deletelocation/{location_id}", response_model=LocationResponse)
def delete_existing_location(location_id: int):
    """Delete a location if it has no inventory"""
    try:
        conn = get_db_connection()
        result = delete_location(conn, location_id)
        conn.close()
        return result
    except Exception as e:
        logger.error(f"Error deleting location: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting location: {str(e)}")
