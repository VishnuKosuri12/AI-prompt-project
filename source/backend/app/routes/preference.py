import logging
from fastapi import APIRouter, Depends, HTTPException
from ..database import get_db_connection
from ..models.preference import (
    UserPreferenceRequest,
    UserPreferenceUpdateRequest,
    UserPreferenceResponse,
    UserPreferenceAck
)
from ..services.preference import get_user_preferences, update_user_preference, delete_user_preferences

logger = logging.getLogger(__name__)
router = APIRouter(tags=["preferences"])

@router.post("/backend/get_user_preferences", response_model=UserPreferenceResponse)
def get_preferences(request: UserPreferenceRequest):
    """Get user preferences endpoint"""
    try:
        conn = get_db_connection()
        preferences = get_user_preferences(conn, request.username, request.key)
        conn.close()
        
        return UserPreferenceResponse(
            success=True,
            preferences=preferences,
            message=f"Found {len(preferences)} preferences for user {request.username}"
        )
    except Exception as e:
        logger.error(f"Error getting user preferences: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting user preferences: {str(e)}")

@router.post("/backend/update_user_preference", response_model=UserPreferenceResponse)
def update_preference(request: UserPreferenceUpdateRequest):
    """Update user preference endpoint"""
    try:
        conn = get_db_connection()
        result = update_user_preference(conn, request.username, request.key, request.value)
        conn.close()
        return result
    except Exception as e:
        logger.error(f"Error updating user preference: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating user preference: {str(e)}")

@router.post("/backend/delete_user_preference", response_model=UserPreferenceAck)
def delete_preferences(request: UserPreferenceRequest):
    """Delete user preferences endpoint"""
    try:
        conn = get_db_connection()
        result = delete_user_preferences(conn, request.username)
        conn.close()
        return result
    except Exception as e:
        logger.error(f"Error deleting user preference: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting user preference: {str(e)}")
