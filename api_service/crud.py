from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Optional, Dict, Any
from datetime import date, datetime, timedelta

import models
import schemas
from cache import CacheManager


# Equipment CRUD operations
def create_equipment(db: Session, equipment: schemas.EquipmentCreate) -> models.Equipment:
    """Create new equipment entry"""
    db_equipment = models.Equipment(
        name=equipment.name,
        category=equipment.category,
        status=equipment.status,
        location=equipment.location,
        serial_number=equipment.serial_number,
        classification_level=equipment.classification_level,
        assigned_unit=equipment.assigned_unit,
        assigned_personnel=equipment.assigned_personnel,
        purchase_date=equipment.purchase_date,
        last_maintenance=equipment.last_maintenance,
        next_maintenance_due=equipment.next_maintenance_due,
        condition_rating=equipment.condition_rating,
    )
    db.add(db_equipment)
    db.commit()
    db.refresh(db_equipment)
    
    # Invalidate related caches
    CacheManager.delete_pattern("equipment_list:*")
    CacheManager.delete_pattern(f"equipment_detail:*/equipment/{db_equipment.id}")
    CacheManager.delete_pattern("statistics:*")
    if db_equipment.assigned_unit:
        CacheManager.delete_pattern(f"equipment_unit:*/equipment/unit/{db_equipment.assigned_unit}*")
    
    return db_equipment


def get_equipment(db: Session, equipment_id: int) -> Optional[models.Equipment]:
    """Get equipment by ID"""
    return db.query(models.Equipment).filter(models.Equipment.id == equipment_id).first()


def get_equipment_list(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    status: Optional[str] = None,
    category: Optional[str] = None,
    classification: Optional[str] = None
) -> List[models.Equipment]:
    """Get list of equipment with filters"""
    query = db.query(models.Equipment)
    
    # Apply filters
    if status:
        query = query.filter(models.Equipment.status == status)
    if category:
        query = query.filter(models.Equipment.category == category)
    if classification:
        query = query.filter(models.Equipment.classification_level == classification)
        
    return query.offset(skip).limit(limit).all()


def get_equipment_count(
    db: Session,
    status: Optional[str] = None,
    category: Optional[str] = None,
    classification: Optional[str] = None
) -> int:
    """Get total count of equipment with filters"""
    query = db.query(func.count(models.Equipment.id))
    
    # Apply filters
    if status:
        query = query.filter(models.Equipment.status == status)
    if category:
        query = query.filter(models.Equipment.category == category)
    if classification:
        query = query.filter(models.Equipment.classification_level == classification)
        
    return query.scalar()


def update_equipment(db: Session, equipment_id: int, equipment: schemas.EquipmentUpdate) -> Optional[models.Equipment]:
    """Update equipment details"""
    db_equipment = get_equipment(db, equipment_id)
    if not db_equipment:
        return None
    
    # Update fields if provided
    update_data = equipment.dict(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            setattr(db_equipment, field, value)
    
    db.commit()
    db.refresh(db_equipment)
    
    # Invalidate related caches
    CacheManager.delete_pattern("equipment_list:*")
    CacheManager.delete_pattern(f"equipment_detail:*/equipment/{equipment_id}")
    CacheManager.delete_pattern("statistics:*")
    if db_equipment.assigned_unit:
        CacheManager.delete_pattern(f"equipment_unit:*/equipment/unit/{db_equipment.assigned_unit}*")
    
    return db_equipment


def delete_equipment(db: Session, equipment_id: int) -> bool:
    """Delete equipment (decommission)"""
    db_equipment = get_equipment(db, equipment_id)
    if not db_equipment:
        return False
    
    # Get the unit ID before deletion for cache invalidation
    unit_id = db_equipment.assigned_unit
    
    db.delete(db_equipment)
    db.commit()
    
    # Invalidate related caches
    CacheManager.delete_pattern("equipment_list:*")
    CacheManager.delete_pattern(f"equipment_detail:*/equipment/{equipment_id}")
    CacheManager.delete_pattern("statistics:*")
    if unit_id:
        CacheManager.delete_pattern(f"equipment_unit:*/equipment/unit/{unit_id}*")
    
    return True


def search_equipment(db: Session, query: str) -> List[models.Equipment]:
    """Search equipment by name, category, or serial number"""
    search_filter = or_(
        models.Equipment.name.ilike(f"%{query}%"),
        models.Equipment.category.cast(String).ilike(f"%{query}%"),
        models.Equipment.serial_number.ilike(f"%{query}%")
    )
    return db.query(models.Equipment).filter(search_filter).all()


def get_equipment_by_unit(
    db: Session,
    unit_id: str,
    skip: int = 0,
    limit: int = 100
) -> List[models.Equipment]:
    """Get equipment by assigned unit"""
    return db.query(models.Equipment).filter(
        models.Equipment.assigned_unit == unit_id
    ).offset(skip).limit(limit).all()


def get_distinct_units(db: Session) -> List[str]:
    """Get a list of distinct unit names that have equipment assigned."""
    units = db.query(models.Equipment.assigned_unit).filter(models.Equipment.assigned_unit.isnot(None)).distinct().all()
    return [unit[0] for unit in units]


def assign_equipment(
    db: Session,
    equipment_id: int,
    assignment: schemas.EquipmentAssignment
) -> Optional[models.Equipment]:
    """Assign equipment to unit or personnel"""
    db_equipment = get_equipment(db, equipment_id)
    if not db_equipment:
        return None
    
    # Store old unit for cache invalidation
    old_unit = db_equipment.assigned_unit
    
    # Update assignment
    if assignment.assigned_unit is not None:
        db_equipment.assigned_unit = assignment.assigned_unit
    if assignment.assigned_personnel is not None:
        db_equipment.assigned_personnel = assignment.assigned_personnel
    
    db.commit()
    db.refresh(db_equipment)
    
    # Invalidate related caches
    CacheManager.delete_pattern("equipment_list:*")
    CacheManager.delete_pattern(f"equipment_detail:*/equipment/{equipment_id}")
    if old_unit:
        CacheManager.delete_pattern(f"equipment_unit:*/equipment/unit/{old_unit}*")
    if db_equipment.assigned_unit:
        CacheManager.delete_pattern(f"equipment_unit:*/equipment/unit/{db_equipment.assigned_unit}*")
    
    return db_equipment


def get_maintenance_equipment(db: Session, skip: int = 0, limit: int = 100) -> List[models.Equipment]:
    """Get equipment due for maintenance"""
    today = date.today()
    thirty_days_from_now = today + timedelta(days=30)
    
    return db.query(models.Equipment).filter(
        and_(
            models.Equipment.next_maintenance_due <= thirty_days_from_now,
            models.Equipment.status != models.EquipmentStatus.decommissioned
        )
    ).order_by(models.Equipment.next_maintenance_due).offset(skip).limit(limit).all()


def get_maintenance_schedule(db: Session) -> (List[models.Equipment], List[models.Equipment]):
    """Get equipment that is overdue for maintenance or due soon."""
    today = date.today()
    thirty_days_from_now = today + timedelta(days=30)

    # Ensure we're using the correct enum values for the status filter
    status_values = [models.EquipmentStatus.operational, models.EquipmentStatus.maintenance]
    
    # Get equipment overdue for maintenance
    overdue = db.query(models.Equipment).filter(
        models.Equipment.next_maintenance_due < today,
        models.Equipment.status.in_(status_values)
    ).order_by(models.Equipment.next_maintenance_due).all()
    
    # If no results, ensure we return an empty list, not None
    if overdue is None:
        overdue = []

    # Get equipment due for maintenance soon
    due_soon = db.query(models.Equipment).filter(
        models.Equipment.next_maintenance_due >= today,
        models.Equipment.next_maintenance_due <= thirty_days_from_now,
        models.Equipment.status.in_(status_values)
    ).order_by(models.Equipment.next_maintenance_due).all()
    
    # If no results, ensure we return an empty list, not None
    if due_soon is None:
        due_soon = []

    return overdue, due_soon


def get_inventory_statistics(db: Session) -> schemas.InventoryStats:
    """Get equipment statistics and readiness reports"""
    total = db.query(func.count(models.Equipment.id)).scalar()
    
    # Status counts
    status_counts = db.query(models.Equipment.status, func.count(models.Equipment.id)).group_by(models.Equipment.status).all()
    status_map = {status.name: count for status, count in status_counts}

    operational = status_map.get('operational', 0)
    maintenance = status_map.get('maintenance', 0)
    damaged = status_map.get('damaged', 0)
    decommissioned = status_map.get('decommissioned', 0)

    # Category counts
    category_counts_query = db.query(models.Equipment.category, func.count(models.Equipment.id)).group_by(models.Equipment.category).all()
    category_counts = {category.name: count for category, count in category_counts_query}

    # Calculate readiness percentage
    active_equipment = total - decommissioned
    readiness_percentage = (operational / active_equipment * 100) if active_equipment > 0 else 0

    return schemas.InventoryStats(
        total_equipment=total,
        operational_count=operational,
        maintenance_count=maintenance,
        damaged_count=damaged,
        decommissioned_count=decommissioned,
        category_counts=category_counts,
        readiness_percentage=round(readiness_percentage, 2)
    )


# Maintenance Log CRUD operations
def create_maintenance_log(db: Session, log: schemas.MaintenanceLogCreate) -> models.MaintenanceLog:
    """Create new maintenance log entry"""
    db_log = models.MaintenanceLog(
        equipment_id=log.equipment_id,
        maintenance_date=log.maintenance_date,
        maintenance_type=log.maintenance_type,
        description=log.description,
        performed_by=log.performed_by,
        notes=log.notes
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    
    # Update equipment last maintenance date
    equipment = get_equipment(db, log.equipment_id)
    if equipment:
        equipment.last_maintenance = log.maintenance_date
        # Set next maintenance due to 6 months from now
        equipment.next_maintenance_due = log.maintenance_date + timedelta(days=180)
        db.commit()
        
        # Invalidate related caches
        CacheManager.delete_pattern("equipment_list:*")
        CacheManager.delete_pattern(f"equipment_detail:*/equipment/{log.equipment_id}")
        CacheManager.delete_pattern("maintenance:*")
    
    return db_log


def get_maintenance_logs(db: Session, equipment_id: int) -> List[models.MaintenanceLog]:
    """Get maintenance logs for specific equipment"""
    return db.query(models.MaintenanceLog).filter(
        models.MaintenanceLog.equipment_id == equipment_id
    ).order_by(models.MaintenanceLog.maintenance_date.desc()).all()
