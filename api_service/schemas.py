from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import date, datetime
from enum import Enum

# Enum definitions
class EquipmentCategory(str, Enum):
    weapons = "weapons"
    vehicles = "vehicles"
    communications = "communications"
    protective_gear = "protective-gear"
    medical = "medical"
    electronics = "electronics"

class EquipmentStatus(str, Enum):
    operational = "operational"
    maintenance = "maintenance"
    damaged = "damaged"
    decommissioned = "decommissioned"

class ClassificationLevel(str, Enum):
    unclassified = "unclassified"
    confidential = "confidential"
    secret = "secret"

# Base Equipment Schema
class EquipmentBase(BaseModel):
    name: str = Field(..., description="Equipment name", min_length=1)
    category: EquipmentCategory
    status: EquipmentStatus
    location: Optional[str] = Field(None, description="Base or unit assignment")
    serial_number: Optional[str] = Field(None, description="Unique serial number")
    classification_level: ClassificationLevel = Field(default=ClassificationLevel.unclassified)
    assigned_unit: Optional[str] = None
    assigned_personnel: Optional[str] = None
    purchase_date: Optional[date] = None
    last_maintenance: Optional[date] = None
    next_maintenance_due: Optional[date] = None
    condition_rating: Optional[int] = Field(None, ge=1, le=5, description="Condition rating (1-5)")
    
    @validator('condition_rating')
    def validate_condition_rating(cls, v):
        if v is not None and (v < 1 or v > 5):
            raise ValueError('Condition rating must be between 1 and 5')
        return v

# Schema for creating equipment
class EquipmentCreate(EquipmentBase):
    pass

# Schema for updating equipment
class EquipmentUpdate(EquipmentBase):
    name: Optional[str] = Field(None, min_length=1)
    category: Optional[EquipmentCategory] = None
    status: Optional[EquipmentStatus] = None
    classification_level: Optional[ClassificationLevel] = None

# Schema for reading equipment
class EquipmentRead(EquipmentBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

# Maintenance Log Schemas
class MaintenanceLogBase(BaseModel):
    equipment_id: int
    maintenance_date: date
    maintenance_type: str
    description: str
    performed_by: str
    notes: Optional[str] = None

class MaintenanceLogCreate(MaintenanceLogBase):
    pass

class MaintenanceLogRead(MaintenanceLogBase):
    id: int
    created_at: datetime
    
    class Config:
        orm_mode = True

# Pagination and response schemas
class PaginatedResponse(BaseModel):
    total: int
    page: int
    page_size: int
    data: List[EquipmentRead]

# Assignment schema
class EquipmentAssignment(BaseModel):
    assigned_unit: Optional[str] = None
    assigned_personnel: Optional[str] = None

# Statistics schema
class InventoryStats(BaseModel):
    total_equipment: int
    operational_count: int
    maintenance_count: int
    damaged_count: int
    decommissioned_count: int
    category_counts: dict
    readiness_percentage: float
