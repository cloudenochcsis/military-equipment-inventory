from sqlalchemy import Column, Integer, String, Date, DateTime, Enum, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from database import Base

class EquipmentCategory(enum.Enum):
    weapons = "weapons"
    vehicles = "vehicles"
    communications = "communications"
    protective_gear = "protective-gear"
    medical = "medical"
    electronics = "electronics"

class EquipmentStatus(enum.Enum):
    operational = "operational"
    maintenance = "maintenance"
    damaged = "damaged"
    decommissioned = "decommissioned"

class ClassificationLevel(enum.Enum):
    unclassified = "unclassified"
    confidential = "confidential"
    secret = "secret"

class Equipment(Base):
    __tablename__ = "equipment"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    category = Column(Enum(EquipmentCategory), nullable=False, index=True)
    status = Column(Enum(EquipmentStatus), nullable=False, index=True)
    location = Column(String, index=True)
    serial_number = Column(String, unique=True, index=True)
    classification_level = Column(Enum(ClassificationLevel), default=ClassificationLevel.unclassified)
    assigned_unit = Column(String, nullable=True, index=True)
    assigned_personnel = Column(String, nullable=True)
    purchase_date = Column(Date, nullable=True)
    last_maintenance = Column(Date, nullable=True)
    next_maintenance_due = Column(Date, nullable=True, index=True)
    condition_rating = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Create indexes for frequently queried fields
    __table_args__ = (
        Index('idx_equipment_status_category', 'status', 'category'),
        Index('idx_equipment_maintenance', 'next_maintenance_due', 'status'),
        Index('idx_equipment_unit_category', 'assigned_unit', 'category'),
    )

class MaintenanceLog(Base):
    __tablename__ = "maintenance_log"
    
    id = Column(Integer, primary_key=True, index=True)
    equipment_id = Column(Integer, ForeignKey("equipment.id", ondelete="CASCADE"), nullable=False)
    maintenance_date = Column(Date, nullable=False)
    maintenance_type = Column(String, nullable=False)
    description = Column(String, nullable=False)
    performed_by = Column(String, nullable=False)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship
    equipment = relationship("Equipment", backref="maintenance_logs")
    
    # Index for quick retrieval of maintenance history
    __table_args__ = (
        Index('idx_maintenance_equipment_date', 'equipment_id', 'maintenance_date'),
    )
