from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class LocationCreateUpdateRequest(BaseModel):
    building_name: str
    lab_room_number: int
    locker_number: int
    location_id: Optional[int] = None

class LocationResponse(BaseModel):
    success: bool
    message: str
    location_id: Optional[int] = None

class LocationCheckResponse(BaseModel):
    success: bool
    has_inventory: bool
    message: Optional[str] = None

class BuildingListResponse(BaseModel):
    success: bool
    buildings: List[str] = []
    message: Optional[str] = None

class LabRoomListResponse(BaseModel):
    success: bool
    lab_rooms: List[int] = []
    message: Optional[str] = None

class LocationsListResponse(BaseModel):
    success: bool
    locations: List[Dict[str, Any]] = []
    message: Optional[str] = None
