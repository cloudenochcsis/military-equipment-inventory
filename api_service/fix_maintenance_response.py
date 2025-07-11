#!/usr/bin/env python3
"""
Script to fix the maintenance endpoint response format in main.py
"""

import re

def fix_maintenance_endpoint():
    # Path to the main.py file
    file_path = "main.py"
    
    try:
        # Read the file content
        with open(file_path, 'r') as file:
            content = file.read()
        
        # Define the pattern to match the maintenance endpoint function
        pattern = r'(@app\.get\("/equipment/maintenance".*?\n.*?get_maintenance_schedule.*?\n.*?try:.*?\n.*?overdue, due_soon = crud\.get_maintenance_schedule\(db=db\).*?\n.*?overdue, due_soon = crud\.get_maintenance_schedule\(db=db\).*?\n.*?# Use the new utility function.*?\n.*?overdue_converted = db_utils\.convert_equipment_objects_to_schema\(overdue\).*?\n.*?due_soon_converted = db_utils\.convert_equipment_objects_to_schema\(due_soon\).*?\n.*?# Combine the converted lists.*?\n.*?return overdue_converted \+ due_soon_converted)'
        
        # Define the replacement with paginated response format
        replacement = r'''@app.get("/equipment/maintenance", tags=["Maintenance"])
@cache_response(expire_seconds=CACHE_TTL["maintenance_schedule"], key_prefix="maintenance_schedule")
async def get_maintenance_schedule(request: Request, db: Session = Depends(get_db)):
    try:
        overdue, due_soon = crud.get_maintenance_schedule(db=db)
        # Use the new utility function to convert ORM objects to schema-compatible dicts
        overdue_converted = db_utils.convert_equipment_objects_to_schema(overdue)
        due_soon_converted = db_utils.convert_equipment_objects_to_schema(due_soon)
        # Combine the converted lists but wrap in a paginated response format
        combined_data = overdue_converted + due_soon_converted
        return {
            "data": combined_data,
            "total": len(combined_data),
            "page": 1,
            "size": len(combined_data),
            "pages": 1
        }'''
        
        # Replace the pattern in the content
        modified_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        
        # Write the modified content back to the file
        with open(file_path, 'w') as file:
            file.write(modified_content)
        
        print("Successfully updated maintenance endpoint response format.")
        return True
    
    except Exception as e:
        print(f"Error updating maintenance endpoint: {str(e)}")
        return False

if __name__ == "__main__":
    fix_maintenance_endpoint()
