#!/usr/bin/env python3
"""
Script to fix the maintenance endpoint in main.py
"""
import re

# Read the main.py file
with open('main.py', 'r') as file:
    content = file.read()

# Define the pattern to match the problematic code
pattern = r'(\s+# Combine and convert each item\n\s+combined_list = overdue \+ due_soon\n\s+return \[convert_equipment_db_to_schema\(e\) for e in combined_list\])'

# Define the replacement code
replacement = """        # Use the new utility function to convert ORM objects to schema-compatible dicts
        overdue_converted = db_utils.convert_equipment_objects_to_schema(overdue)
        due_soon_converted = db_utils.convert_equipment_objects_to_schema(due_soon)
        # Combine the converted lists
        return overdue_converted + due_soon_converted"""

# Replace the problematic code with the fixed code
fixed_content = re.sub(pattern, replacement, content)

# Write the fixed content back to the file
with open('main.py', 'w') as file:
    file.write(fixed_content)

print("Maintenance endpoint fixed successfully!")
