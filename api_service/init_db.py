#!/usr/bin/env python3
"""
Database initialization script
This script will drop and recreate the database tables from scratch
"""
import os
import sys
from sqlalchemy_utils import database_exists, create_database, drop_database
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# Import models to ensure they're registered with Base
from models import Base, Equipment, MaintenanceLog
from database import engine, get_db

def init_db():
    """Initialize the database by dropping and recreating tables"""
    print("Starting database initialization...")
    
    try:
        # Drop all tables
        print("Dropping existing tables...")
        Base.metadata.drop_all(bind=engine)
        
        # Create all tables
        print("Creating tables...")
        Base.metadata.create_all(bind=engine)
        
        print("Database initialization complete!")
        return True
    except SQLAlchemyError as e:
        print(f"Error initializing database: {str(e)}")
        return False

if __name__ == "__main__":
    success = init_db()
    sys.exit(0 if success else 1)
