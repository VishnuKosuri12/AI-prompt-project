from pydantic import BaseModel
from typing import Optional, Dict

class UserPreferenceRequest(BaseModel):
    username: str
    key: Optional[str] = None

class UserPreferenceUpdateRequest(BaseModel):
    username: str
    key: str
    value: str

class UserPreferenceResponse(BaseModel):
    success: bool
    preferences: Dict[str, str] = {}
    message: Optional[str] = None

class UserPreferenceAck(BaseModel):
    success: bool
    message: str