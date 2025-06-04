from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class Chemical(BaseModel):
    id: int
    name: str
    unit_of_measure: str
    quantity: float
    reorder_quantity: float
    building_name: str
    lab_room_number: int
    locker_number: int
    cas_number: Optional[str] = None
    chemical_formula: Optional[str] = None
    signal_word: Optional[str] = None
    physical_state: Optional[str] = None
    hazard_classification: Optional[str] = None
    chemical_description: Optional[str] = None
    molecular_weight: Optional[str] = None
    sds_link: Optional[str] = None

class ChemicalDetailsResponse(BaseModel):
    success: bool
    chemical: Optional[Dict[str, Any]] = None
    message: Optional[str] = None

class InventoryUpdateRequest(BaseModel):
    inventory_id: int
    quantity: float = Field(..., gt=0)
    action: str  # 'add' or 'remove'

class InventoryUpdateResponse(BaseModel):
    success: bool
    new_quantity: float
    message: Optional[str] = None

class ChemSearchRequest(BaseModel):
    name: Optional[str] = None
    building_name: Optional[str] = None
    lab_room_number: Optional[int] = None
    locker_number: Optional[int] = None
    hazard_classification: Optional[str] = None

class ChemSearchResponse(BaseModel):
    success: bool
    results: List[Dict[str, Any]] = []
    message: Optional[str] = None

class ReorderNotifUser(BaseModel):
    username: str
    email: str
    chemicals: List[Dict[str, Any]] = []

class ReorderNotifResponse(BaseModel):
    success: bool
    users: List[ReorderNotifUser] = []
    message: Optional[str] = None
