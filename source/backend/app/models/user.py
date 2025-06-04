from pydantic import BaseModel
from typing import Optional, Dict, List, Any

class UserRequest(BaseModel):
    username: str
    password: str
    email: str
    role: str

class UserInfoRequest(BaseModel):
    username: str

class UserInfoResponse(BaseModel):
    success: bool
    username: str
    email: str
    role: str
    message: Optional[str] = None

class UserResponse(BaseModel):
    success: bool
    message: str

class UsersListResponse(BaseModel):
    success: bool
    users: List[Dict[str, Any]] = []
    message: Optional[str] = None

class RolesListResponse(BaseModel):
    success: bool
    roles: List[str] = []
    message: Optional[str] = None
