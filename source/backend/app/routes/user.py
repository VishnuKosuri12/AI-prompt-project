import logging
from fastapi import APIRouter, Depends, HTTPException
from ..database import get_db_connection
from ..models.user import (
    UserRequest,
    UserInfoRequest,
    UserInfoResponse,
    UserResponse,
    UsersListResponse,
    RolesListResponse
)
from ..services.user import (
    create_user,
    get_user_info,
    update_user,
    get_all_users,
    get_roles,
    delete_user
)

logger = logging.getLogger(__name__)
router = APIRouter(tags=["users"])

@router.post("/backend/createuser", response_model=UserResponse)
def create_new_user(request: UserRequest):
    """Create user endpoint"""
    try:
        conn = get_db_connection()
        result = create_user(conn, request.username, request.password, request.email, request.role)
        conn.close()
        return result
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating user: {str(e)}")

@router.post("/backend/get_user_info", response_model=UserInfoResponse)
def get_user_information(request: UserInfoRequest):
    """Get user information endpoint"""
    try:
        conn = get_db_connection()
        result = get_user_info(conn, request.username)
        conn.close()
        return result
    except Exception as e:
        logger.error(f"Error getting user info: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting user info: {str(e)}")

@router.post("/backend/updateuser", response_model=UserResponse)
def update_existing_user(request: UserRequest):
    """Update user endpoint"""
    try:
        conn = get_db_connection()
        result = update_user(conn, request.username, request.email, request.role, request.password)
        conn.close()
        return result
    except Exception as e:
        logger.error(f"Error updating user: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating user: {str(e)}")

@router.get("/backend/users", response_model=UsersListResponse)
def get_all_system_users():
    """Get all users endpoint"""
    try:
        conn = get_db_connection()
        result = get_all_users(conn)
        conn.close()
        return result
    except Exception as e:
        logger.error(f"Error getting users: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting users: {str(e)}")

@router.get("/backend/roles", response_model=RolesListResponse)
def get_system_roles():
    """Get a list of all available roles"""
    try:
        conn = get_db_connection()
        result = get_roles(conn)
        conn.close()
        return result
    except Exception as e:
        logger.error(f"Error getting roles: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting roles: {str(e)}")

@router.post("/backend/deleteuser", response_model=UserResponse)
def delete_existing_user(request: UserInfoRequest):
    """Delete user endpoint"""
    try:
        conn = get_db_connection()
        result = delete_user(conn, request.username)
        conn.close()
        return result
    except Exception as e:
        logger.error(f"Error deleting user: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting user: {str(e)}")
