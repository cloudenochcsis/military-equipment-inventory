"""
Database utilities for handling equipment data with proper enum conversion.
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

import models
import schemas
import crud
from enum_converter import convert_equipment_db_to_schema


def get_equipment_with_enum_conversion(db: Session, equipment_id: int) -> Optional[Dict[str, Any]]:
    """
    Get equipment by ID with proper enum conversion for API schema compatibility
    """
    db_equipment = crud.get_equipment(db=db, equipment_id=equipment_id)
    if not db_equipment:
        return None
    
    # Convert to dict for manipulation
    equipment_dict = {c.name: getattr(db_equipment, c.name) for c in db_equipment.__table__.columns}
    
    # Convert enum values to match Pydantic schema expectations
    return convert_equipment_db_to_schema(equipment_dict)


def get_equipment_list_with_enum_conversion(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    status: Optional[str] = None,
    category: Optional[str] = None,
    classification: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Get list of equipment with filters and proper enum conversion for API schema compatibility
    """
    db_equipment_list = crud.get_equipment_list(
        db=db, 
        skip=skip, 
        limit=limit, 
        status=status, 
        category=category, 
        classification=classification
    )
    
    # Convert each equipment item
    result = []
    for db_equipment in db_equipment_list:
        # Convert to dict for manipulation
        equipment_dict = {c.name: getattr(db_equipment, c.name) for c in db_equipment.__table__.columns}
        
        # Convert enum values to match Pydantic schema expectations
        converted_equipment = convert_equipment_db_to_schema(equipment_dict)
        result.append(converted_equipment)
    
    return result
"""
Temporary fix for maintenance endpoint
"""
from typing import List, Dict, Any
from sqlalchemy.orm import Session

import models
import schemas
import crud
from enum_converter import convert_equipment_db_to_schema

def convert_equipment_objects_to_schema(equipment_list: List) -> List[Dict[str, Any]]:
    """
    Convert a list of equipment ORM objects to schema-compatible dictionaries
    
    Args:
        equipment_list: List of equipment ORM objects
        
    Returns:
        List of converted equipment dictionaries
    """
    result = []
    for equipment in equipment_list:
        # Convert ORM object to dict
        equipment_dict = {c.name: getattr(equipment, c.name) for c in equipment.__table__.columns}
        
        # Convert enum values to match Pydantic schema expectations
        converted_equipment = convert_equipment_db_to_schema(equipment_dict)
        result.append(converted_equipment)
    
    return result
