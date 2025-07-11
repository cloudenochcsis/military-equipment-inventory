#!/usr/bin/env python3
"""
Seed data script for Military Equipment Inventory System
This script populates the database with sample equipment and maintenance logs
"""
import os
import sys
import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import random
from typing import List

from database import SessionLocal, engine
import models

# Create sample data
def create_sample_equipment(db: Session) -> List[int]:
    """
    Create sample equipment records and return their IDs
    """
    print("Creating sample equipment data...")
    equipment_ids = []
    
    # Weapons
    weapons = [
        {
            "name": "M4A1 Carbine",
            "category": models.EquipmentCategory.weapons,
            "status": models.EquipmentStatus.operational,
            "location": "Armory A",
            "serial_number": "W-10045-AR",
            "classification_level": models.ClassificationLevel.unclassified,
            "assigned_unit": "Alpha Company",
            "assigned_personnel": "Sgt. Johnson",
            "purchase_date": datetime.date(2022, 3, 15),
            "last_maintenance": datetime.date(2025, 5, 20),
            "next_maintenance_due": datetime.date(2025, 8, 20),
            "condition_rating": 5
        },
        {
            "name": "M240B Machine Gun",
            "category": models.EquipmentCategory.weapons,
            "status": models.EquipmentStatus.maintenance,
            "location": "Maintenance Bay 2",
            "serial_number": "W-30291-MG",
            "classification_level": models.ClassificationLevel.unclassified,
            "assigned_unit": "Bravo Company",
            "assigned_personnel": None,
            "purchase_date": datetime.date(2021, 7, 10),
            "last_maintenance": datetime.date(2025, 4, 15),
            "next_maintenance_due": datetime.date(2025, 7, 15),
            "condition_rating": 3
        },
        {
            "name": "M107 Sniper Rifle",
            "category": models.EquipmentCategory.weapons,
            "status": models.EquipmentStatus.operational,
            "location": "Special Ops Armory",
            "serial_number": "W-50087-SR",
            "classification_level": models.ClassificationLevel.confidential,
            "assigned_unit": "Recon Team",
            "assigned_personnel": "SSgt. Martinez",
            "purchase_date": datetime.date(2023, 1, 5),
            "last_maintenance": datetime.date(2025, 6, 10),
            "next_maintenance_due": datetime.date(2025, 9, 10),
            "condition_rating": 5
        }
    ]
    
    # Vehicles
    vehicles = [
        {
            "name": "HMMWV (Humvee)",
            "category": models.EquipmentCategory.vehicles,
            "status": models.EquipmentStatus.operational,
            "location": "Motor Pool B",
            "serial_number": "V-85623-HV",
            "classification_level": models.ClassificationLevel.unclassified,
            "assigned_unit": "Delta Company",
            "assigned_personnel": None,
            "purchase_date": datetime.date(2020, 5, 12),
            "last_maintenance": datetime.date(2025, 3, 1),
            "next_maintenance_due": datetime.date(2025, 9, 1),
            "condition_rating": 4
        },
        {
            "name": "M1A2 Abrams Tank",
            "category": models.EquipmentCategory.vehicles,
            "status": models.EquipmentStatus.operational,
            "location": "Armor Battalion HQ",
            "serial_number": "V-12785-AT",
            "classification_level": models.ClassificationLevel.confidential,
            "assigned_unit": "1st Armor Battalion",
            "assigned_personnel": "Lt. Rodriguez",
            "purchase_date": datetime.date(2018, 11, 3),
            "last_maintenance": datetime.date(2025, 4, 25),
            "next_maintenance_due": datetime.date(2025, 7, 25),
            "condition_rating": 5
        },
        {
            "name": "MQ-9 Reaper Drone",
            "category": models.EquipmentCategory.vehicles,
            "status": models.EquipmentStatus.damaged,
            "location": "Repair Facility",
            "serial_number": "V-30987-DR",
            "classification_level": models.ClassificationLevel.secret,
            "assigned_unit": "Air Support Division",
            "assigned_personnel": None,
            "purchase_date": datetime.date(2021, 2, 17),
            "last_maintenance": datetime.date(2025, 1, 5),
            "next_maintenance_due": datetime.date(2025, 7, 5),
            "condition_rating": 2
        }
    ]
    
    # Communications
    communications = [
        {
            "name": "AN/PRC-158 Radio",
            "category": models.EquipmentCategory.communications,
            "status": models.EquipmentStatus.operational,
            "location": "Comms Center",
            "serial_number": "C-45621-RD",
            "classification_level": models.ClassificationLevel.confidential,
            "assigned_unit": "Comm Battalion",
            "assigned_personnel": "Cpl. Davis",
            "purchase_date": datetime.date(2023, 6, 22),
            "last_maintenance": datetime.date(2025, 5, 15),
            "next_maintenance_due": datetime.date(2025, 11, 15),
            "condition_rating": 5
        },
        {
            "name": "Tactical Satellite Terminal",
            "category": models.EquipmentCategory.communications,
            "status": models.EquipmentStatus.operational,
            "location": "Command HQ",
            "serial_number": "C-12098-ST",
            "classification_level": models.ClassificationLevel.secret,
            "assigned_unit": "Command Staff",
            "assigned_personnel": "Maj. Thompson",
            "purchase_date": datetime.date(2022, 9, 8),
            "last_maintenance": datetime.date(2025, 6, 1),
            "next_maintenance_due": datetime.date(2025, 12, 1),
            "condition_rating": 5
        }
    ]
    
    # Protective Gear
    protective_gear = [
        {
            "name": "Enhanced Combat Helmet",
            "category": models.EquipmentCategory.protective_gear,
            "status": models.EquipmentStatus.operational,
            "location": "Supply Room A",
            "serial_number": "P-78541-CH",
            "classification_level": models.ClassificationLevel.unclassified,
            "assigned_unit": "Echo Company",
            "assigned_personnel": "PFC. Miller",
            "purchase_date": datetime.date(2024, 1, 10),
            "last_maintenance": datetime.date(2025, 1, 10),
            "next_maintenance_due": datetime.date(2026, 1, 10),
            "condition_rating": 5
        },
        {
            "name": "IOTV Body Armor",
            "category": models.EquipmentCategory.protective_gear,
            "status": models.EquipmentStatus.maintenance,
            "location": "Maintenance Bay 1",
            "serial_number": "P-36521-BA",
            "classification_level": models.ClassificationLevel.unclassified,
            "assigned_unit": "Foxtrot Company",
            "assigned_personnel": None,
            "purchase_date": datetime.date(2022, 11, 25),
            "last_maintenance": datetime.date(2024, 11, 25),
            "next_maintenance_due": datetime.date(2025, 11, 25),
            "condition_rating": 3
        }
    ]
    
    # Medical
    medical = [
        {
            "name": "Combat Medic Backpack",
            "category": models.EquipmentCategory.medical,
            "status": models.EquipmentStatus.operational,
            "location": "Medical Bay",
            "serial_number": "M-45123-MB",
            "classification_level": models.ClassificationLevel.unclassified,
            "assigned_unit": "Medical Corps",
            "assigned_personnel": "Medic Wilson",
            "purchase_date": datetime.date(2023, 8, 15),
            "last_maintenance": datetime.date(2025, 2, 15),
            "next_maintenance_due": datetime.date(2025, 8, 15),
            "condition_rating": 4
        },
        {
            "name": "Portable Ultrasound",
            "category": models.EquipmentCategory.medical,
            "status": models.EquipmentStatus.operational,
            "location": "Field Hospital",
            "serial_number": "M-85412-US",
            "classification_level": models.ClassificationLevel.unclassified,
            "assigned_unit": "MASH Unit",
            "assigned_personnel": "Dr. Garcia",
            "purchase_date": datetime.date(2023, 5, 3),
            "last_maintenance": datetime.date(2025, 5, 3),
            "next_maintenance_due": datetime.date(2025, 11, 3),
            "condition_rating": 5
        }
    ]
    
    # Electronics
    electronics = [
        {
            "name": "Tactical Drone Controller",
            "category": models.EquipmentCategory.electronics,
            "status": models.EquipmentStatus.operational,
            "location": "Operations Center",
            "serial_number": "E-78956-DC",
            "classification_level": models.ClassificationLevel.confidential,
            "assigned_unit": "Drone Team",
            "assigned_personnel": "Sgt. Adams",
            "purchase_date": datetime.date(2024, 2, 28),
            "last_maintenance": datetime.date(2025, 6, 15),
            "next_maintenance_due": datetime.date(2025, 12, 15),
            "condition_rating": 5
        },
        {
            "name": "Thermal Imaging System",
            "category": models.EquipmentCategory.electronics,
            "status": models.EquipmentStatus.damaged,
            "location": "Repair Shop",
            "serial_number": "E-36521-TI",
            "classification_level": models.ClassificationLevel.confidential,
            "assigned_unit": "Recon Team",
            "assigned_personnel": None,
            "purchase_date": datetime.date(2022, 7, 19),
            "last_maintenance": datetime.date(2025, 1, 10),
            "next_maintenance_due": datetime.date(2025, 7, 10),
            "condition_rating": 2
        },
        {
            "name": "Tactical Laptop",
            "category": models.EquipmentCategory.electronics,
            "status": models.EquipmentStatus.decommissioned,
            "location": "Storage Warehouse",
            "serial_number": "E-95412-LT",
            "classification_level": models.ClassificationLevel.secret,
            "assigned_unit": None,
            "assigned_personnel": None,
            "purchase_date": datetime.date(2020, 3, 12),
            "last_maintenance": datetime.date(2023, 10, 5),
            "next_maintenance_due": None,
            "condition_rating": 1
        }
    ]
    
    # Combine all equipment
    all_equipment = weapons + vehicles + communications + protective_gear + medical + electronics
    
    # Add to database
    for equip_data in all_equipment:
        try:
            equipment = models.Equipment(**equip_data)
            db.add(equipment)
            db.commit()
            db.refresh(equipment)
            equipment_ids.append(equipment.id)
            print(f"Added equipment: {equipment.name} (ID: {equipment.id})")
        except SQLAlchemyError as e:
            db.rollback()
            print(f"Error adding equipment {equip_data['name']}: {str(e)}")
    
    return equipment_ids

def create_sample_maintenance_logs(db: Session, equipment_ids: List[int]):
    """
    Create sample maintenance logs for equipment
    """
    print("\nCreating sample maintenance logs...")
    maintenance_types = [
        "Routine Inspection", 
        "Parts Replacement",
        "Calibration",
        "Cleaning",
        "Firmware Update",
        "Repair",
        "Overhaul"
    ]
    
    personnel = [
        "Sgt. Johnson",
        "Tech. Williams",
        "Spc. Brown",
        "CW2 Smith",
        "Cpl. Rodriguez"
    ]
    
    # For each equipment, create 1-3 maintenance logs
    for equip_id in equipment_ids:
        # Skip some equipment to have varied maintenance history
        if random.random() < 0.2:
            continue
            
        # Get the equipment to set realistic dates
        equipment = db.query(models.Equipment).filter(models.Equipment.id == equip_id).first()
        if not equipment:
            continue
            
        # Determine number of maintenance logs
        log_count = random.randint(1, 3)
        
        for i in range(log_count):
            # Generate a date between purchase date and now
            if equipment.purchase_date:
                days_since_purchase = (datetime.date.today() - equipment.purchase_date).days
                if days_since_purchase <= 0:
                    continue
                    
                days_ago = random.randint(0, days_since_purchase)
                maint_date = datetime.date.today() - datetime.timedelta(days=days_ago)
                
                # Make sure maintenance date is not in the future
                if maint_date > datetime.date.today():
                    maint_date = datetime.date.today()
                
                maint_data = {
                    "equipment_id": equip_id,
                    "maintenance_date": maint_date,
                    "maintenance_type": random.choice(maintenance_types),
                    "description": f"Performed {random.choice(maintenance_types).lower()} on equipment",
                    "performed_by": random.choice(personnel),
                    "notes": f"Equipment is in {['poor', 'fair', 'good', 'excellent'][random.randint(0, 3)]} condition after maintenance."
                }
                
                try:
                    maint_log = models.MaintenanceLog(**maint_data)
                    db.add(maint_log)
                    db.commit()
                    print(f"Added maintenance log for equipment ID {equip_id}: {maint_data['maintenance_type']}")
                except SQLAlchemyError as e:
                    db.rollback()
                    print(f"Error adding maintenance log for equipment ID {equip_id}: {str(e)}")

def seed_database():
    """
    Main function to seed the database
    """
    print("Starting database seeding process...")
    
    # Create a database session
    db = SessionLocal()
    
    try:
        # Check if database already has data to avoid duplicates
        existing_count = db.query(models.Equipment).count()
        if existing_count > 0:
            print(f"Database already contains {existing_count} equipment records.")
            confirm = input("Do you want to proceed and add more data? (y/n): ")
            if confirm.lower() != 'y':
                print("Seeding cancelled.")
                return
        
        # Create equipment and get their IDs
        equipment_ids = create_sample_equipment(db)
        
        # Create maintenance logs
        create_sample_maintenance_logs(db, equipment_ids)
        
        print("\nDatabase seeding completed successfully!")
        print(f"Added {len(equipment_ids)} equipment records with maintenance logs")
        
    except Exception as e:
        print(f"Error during database seeding: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
