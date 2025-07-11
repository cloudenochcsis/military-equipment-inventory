#!/usr/bin/env python3
"""
Enum value converter for Military Equipment Inventory API.
This module handles the conversion between database enum values and Pydantic schema values.
"""
from typing import Dict, Any, Type
import models
import schemas

def convert_db_to_schema_enum(db_value: Any, enum_class: Type) -> Any:
    """
    Convert a database enum value to the corresponding Pydantic schema enum value.
    
    Args:
        db_value: Value from the database (could be string or enum)
        enum_class: Target Pydantic enum class
    
    Returns:
        The corresponding enum value for the schema
    """
    # If the input is already an enum instance
    if hasattr(db_value, 'name') and hasattr(db_value, 'value'):
        # Extract the string value from the enum
        db_value = db_value.value
    
    # Make sure we're working with a string
    if not isinstance(db_value, str):
        return None
    
    # Handle special cases for different hyphenation styles
    if db_value == "protective-gear" and hasattr(enum_class, "protective_gear"):
        return enum_class.protective_gear
    
    # Try direct mapping first
    try:
        return enum_class(db_value)
    except ValueError:
        # Try alternative mappings (convert hyphens to underscores, etc.)
        normalized_value = db_value.replace('-', '_')
        for enum_value in enum_class:
            if enum_value.name == normalized_value or enum_value.value == db_value:
                return enum_value
    
    # If all else fails, raise an exception
    raise ValueError(f"Could not convert '{db_value}' to enum {enum_class.__name__}")

def convert_equipment_db_to_schema(db_equipment: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert equipment data from database representation to schema representation.
    
    Args:
        db_equipment: Equipment data from database
    
    Returns:
        Equipment data suitable for Pydantic schema
    """
    result = dict(db_equipment)
    
    # Convert enum fields
    if "category" in result and result["category"] is not None:
        result["category"] = convert_db_to_schema_enum(result["category"], schemas.EquipmentCategory)
    
    if "status" in result and result["status"] is not None:
        result["status"] = convert_db_to_schema_enum(result["status"], schemas.EquipmentStatus)
    
    if "classification_level" in result and result["classification_level"] is not None:
        result["classification_level"] = convert_db_to_schema_enum(
            result["classification_level"], schemas.ClassificationLevel
        )
    
    return result
