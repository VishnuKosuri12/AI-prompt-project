from pydantic import BaseModel
from typing import Optional, Dict

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    success: bool
    role: Optional[str] = None
    message: Optional[str] = None
    preferences: Optional[Dict[str, str]] = None

class UserPswdRequest(BaseModel):
    username: str
    old_password: str
    new_password: str

class PasswordResetRequest(BaseModel):
    username: str

class PasswordResetResponse(BaseModel):
    success: bool
    message: Optional[str] = None
