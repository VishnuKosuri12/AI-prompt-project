import logging
from fastapi import APIRouter, Depends, HTTPException
from ..database import get_db_connection
from ..models.auth import (
    LoginRequest, 
    LoginResponse, 
    UserPswdRequest, 
    PasswordResetRequest,
    PasswordResetResponse,
)
from ..models.user import UserResponse
from ..services.auth import login_user, update_password, set_password_reset

logger = logging.getLogger(__name__)
router = APIRouter(tags=["authentication"])

@router.post("/backend/login", response_model=LoginResponse)
def login(request: LoginRequest):
    """Login endpoint"""
    try:
        conn = get_db_connection()
        result = login_user(conn, request.username, request.password)
        conn.close()
        return result
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Login error: {str(e)}")

@router.post("/backend/updatepassword", response_model=UserResponse)
def update_user_password(request: UserPswdRequest):
    """Update user password endpoint"""
    try:
        conn = get_db_connection()
        result = update_password(conn, request.username, request.old_password, request.new_password)
        conn.close()
        return result
    except Exception as e:
        logger.error(f"Error updating password: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating password: {str(e)}")

@router.post("/backend/set_password_reset", response_model=PasswordResetResponse)
def password_reset(request: PasswordResetRequest):
    """Set password reset flag for a user"""
    try:
        conn = get_db_connection()
        result = set_password_reset(conn, request.username)
        conn.close()
        return result
    except Exception as e:
        logger.error(f"Error setting password reset: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error setting password reset: {str(e)}")
