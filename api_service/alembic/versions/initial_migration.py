"""Initial migration

Revision ID: 52b10aa37f21
Revises: 
Create Date: 2023-05-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '52b10aa37f21'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create enum types
    equipment_category = postgresql.ENUM('weapons', 'vehicles', 'communications', 'protective-gear', 'medical', 'electronics', name='equipmentcategory')
    equipment_category.create(op.get_bind())
    
    equipment_status = postgresql.ENUM('operational', 'maintenance', 'damaged', 'decommissioned', name='equipmentstatus')
    equipment_status.create(op.get_bind())
    
    classification_level = postgresql.ENUM('unclassified', 'confidential', 'secret', name='classificationlevel')
    classification_level.create(op.get_bind())
    
    # Create equipment table
    op.create_table(
        'equipment',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('category', sa.Enum('weapons', 'vehicles', 'communications', 'protective-gear', 'medical', 'electronics', name='equipmentcategory'), nullable=False),
        sa.Column('status', sa.Enum('operational', 'maintenance', 'damaged', 'decommissioned', name='equipmentstatus'), nullable=False),
        sa.Column('location', sa.String(), nullable=True),
        sa.Column('serial_number', sa.String(), nullable=True),
        sa.Column('classification_level', sa.Enum('unclassified', 'confidential', 'secret', name='classificationlevel'), nullable=True),
        sa.Column('assigned_unit', sa.String(), nullable=True),
        sa.Column('assigned_personnel', sa.String(), nullable=True),
        sa.Column('purchase_date', sa.Date(), nullable=True),
        sa.Column('last_maintenance', sa.Date(), nullable=True),
        sa.Column('next_maintenance_due', sa.Date(), nullable=True),
        sa.Column('condition_rating', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create maintenance_log table
    op.create_table(
        'maintenance_log',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('equipment_id', sa.Integer(), nullable=False),
        sa.Column('maintenance_date', sa.Date(), nullable=False),
        sa.Column('maintenance_type', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=False),
        sa.Column('performed_by', sa.String(), nullable=False),
        sa.Column('notes', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['equipment_id'], ['equipment.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('idx_equipment_name', 'equipment', ['name'])
    op.create_index('idx_equipment_category', 'equipment', ['category'])
    op.create_index('idx_equipment_status', 'equipment', ['status'])
    op.create_index('idx_equipment_location', 'equipment', ['location'])
    op.create_index('idx_equipment_serial', 'equipment', ['serial_number'], unique=True)
    op.create_index('idx_equipment_unit', 'equipment', ['assigned_unit'])
    op.create_index('idx_equipment_next_maintenance', 'equipment', ['next_maintenance_due'])
    op.create_index('idx_equipment_status_category', 'equipment', ['status', 'category'])
    op.create_index('idx_equipment_maintenance', 'equipment', ['next_maintenance_due', 'status'])
    op.create_index('idx_equipment_unit_category', 'equipment', ['assigned_unit', 'category'])
    op.create_index('idx_maintenance_equipment_date', 'maintenance_log', ['equipment_id', 'maintenance_date'])


def downgrade():
    # Drop indexes
    op.drop_index('idx_maintenance_equipment_date', 'maintenance_log')
    op.drop_index('idx_equipment_unit_category', 'equipment')
    op.drop_index('idx_equipment_maintenance', 'equipment')
    op.drop_index('idx_equipment_status_category', 'equipment')
    op.drop_index('idx_equipment_next_maintenance', 'equipment')
    op.drop_index('idx_equipment_unit', 'equipment')
    op.drop_index('idx_equipment_serial', 'equipment')
    op.drop_index('idx_equipment_location', 'equipment')
    op.drop_index('idx_equipment_status', 'equipment')
    op.drop_index('idx_equipment_category', 'equipment')
    op.drop_index('idx_equipment_name', 'equipment')
    
    # Drop tables
    op.drop_table('maintenance_log')
    op.drop_table('equipment')
    
    # Drop enums
    postgresql.ENUM(name='classificationlevel').drop(op.get_bind())
    postgresql.ENUM(name='equipmentstatus').drop(op.get_bind())
    postgresql.ENUM(name='equipmentcategory').drop(op.get_bind())
