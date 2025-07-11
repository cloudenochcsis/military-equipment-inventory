"""
Fixed implementation of the maintenance endpoint
"""

@app.get("/equipment/maintenance", response_model=List[schemas.EquipmentRead], tags=["Maintenance"])
@cache_response(expire_seconds=CACHE_TTL["maintenance_schedule"], key_prefix="maintenance_schedule")
async def get_maintenance_schedule(request: Request, db: Session = Depends(get_db)):
    try:
        overdue, due_soon = crud.get_maintenance_schedule(db=db)
        # Use the new utility function to convert ORM objects to schema-compatible dicts
        overdue_converted = db_utils.convert_equipment_objects_to_schema(overdue)
        due_soon_converted = db_utils.convert_equipment_objects_to_schema(due_soon)
        # Combine the converted lists
        return overdue_converted + due_soon_converted
    except Exception as e:
        logger.error(f"Error getting maintenance schedule: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get maintenance schedule")
