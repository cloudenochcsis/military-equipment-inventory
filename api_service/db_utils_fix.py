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
