"""
Tests for the Django forms in the equipment app
"""
from datetime import date, timedelta
from django.test import TestCase
from django.forms import ValidationError

from equipment.forms import (
    EquipmentForm, MaintenanceLogForm, EquipmentAssignmentForm, SearchForm
)


class EquipmentFormTest(TestCase):
    """Test the equipment form validation and functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.valid_data = {
            'name': 'M4A1 Carbine',
            'category': 'weapons',
            'status': 'operational',
            'location': 'Alpha Base',
            'serial_number': 'M4A1-12345-XYZ',
            'classification_level': 'unclassified',
            'assigned_unit': '1st Infantry Division',
            'assigned_personnel': 'Sergeant J. Smith',
            'purchase_date': '2023-01-15',
            'last_maintenance': '2023-05-20',
            'next_maintenance_due': '2023-08-20',
            'condition_rating': 4
        }
    
    def test_valid_equipment_form(self):
        """Test form with valid data"""
        form = EquipmentForm(data=self.valid_data)
        self.assertTrue(form.is_valid())
    
    def test_invalid_serial_number(self):
        """Test form with invalid serial number"""
        # Create invalid data with a very short serial number
        invalid_data = self.valid_data.copy()
        invalid_data['serial_number'] = '123'
        
        form = EquipmentForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('serial_number', form.errors)
    
    def test_invalid_category(self):
        """Test form with invalid category"""
        invalid_data = self.valid_data.copy()
        invalid_data['category'] = 'invalid_category'
        
        form = EquipmentForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('category', form.errors)
    
    def test_invalid_status(self):
        """Test form with invalid status"""
        invalid_data = self.valid_data.copy()
        invalid_data['status'] = 'invalid_status'
        
        form = EquipmentForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('status', form.errors)
    
    def test_invalid_classification(self):
        """Test form with invalid classification"""
        invalid_data = self.valid_data.copy()
        invalid_data['classification_level'] = 'top_secret'
        
        form = EquipmentForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('classification_level', form.errors)
    
    def test_invalid_condition_rating(self):
        """Test form with invalid condition rating"""
        # Rating should be 1-5
        invalid_data = self.valid_data.copy()
        invalid_data['condition_rating'] = 6

        form = EquipmentForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('condition_rating', form.errors)
    
    def test_required_fields(self):
        """Test required fields validation"""
        required_fields = ['name', 'category', 'status']

        for field in required_fields:
            invalid_data = self.valid_data.copy()
            invalid_data.pop(field)

            form = EquipmentForm(data=invalid_data)
            self.assertFalse(form.is_valid())
            self.assertIn(field, form.errors)
    
    def test_maintenance_date_validation(self):
        """Test maintenance date validation"""
        # Last maintenance should not be in the future
        invalid_data = self.valid_data.copy()
        tomorrow = date.today() + timedelta(days=1)
        invalid_data['last_maintenance'] = tomorrow.strftime('%Y-%m-%d')

        form = EquipmentForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('last_maintenance', form.errors)


class MaintenanceLogFormTest(TestCase):
    """Test the maintenance log form validation and functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.valid_data = {
            'maintenance_date': date.today().strftime('%Y-%m-%d'),
            'maintenance_type': 'preventive',
            'description': 'Routine check-up',
            'performed_by': 'Tech. Sgt. Reynolds',
            'notes': 'All systems nominal.'
        }
    
    def test_valid_maintenance_form(self):
        """Test form with valid data"""
        form = MaintenanceLogForm(data=self.valid_data)
        self.assertTrue(form.is_valid())
    
    def test_invalid_maintenance_type(self):
        """Test form with invalid maintenance type"""
        invalid_data = self.valid_data.copy()
        invalid_data['maintenance_type'] = 'invalid_type'

        form = MaintenanceLogForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('maintenance_type', form.errors)
    
    def test_required_fields(self):
        """Test required fields validation"""
        required_fields = ['maintenance_date', 'maintenance_type', 'description', 'performed_by']

        for field in required_fields:
            invalid_data = self.valid_data.copy()
            invalid_data.pop(field)

            form = MaintenanceLogForm(data=invalid_data)
            self.assertFalse(form.is_valid())
            self.assertIn(field, form.errors)
    
    def test_future_date_validation(self):
        """Test future date validation for maintenance date"""
        # Future dates should not be allowed
        invalid_data = self.valid_data.copy()
        tomorrow = date.today() + timedelta(days=1)
        invalid_data['maintenance_date'] = tomorrow.strftime('%Y-%m-%d')

        form = MaintenanceLogForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('maintenance_date', form.errors)


class EquipmentAssignmentFormTest(TestCase):
    """Test the equipment assignment form validation and functionality"""

    def setUp(self):
        """Set up test data"""
        self.units = ['1st Infantry Division', '101st Airborne']
        self.valid_data = {
            'assigned_unit': '1st Infantry Division',
            'assigned_personnel': 'Sergeant J. Smith',
        }

    def test_valid_assignment_form(self):
        """Test form with valid data"""
        form = EquipmentAssignmentForm(data=self.valid_data, units=self.units)
        self.assertTrue(form.is_valid())

    def test_empty_assignment_is_valid(self):
        """Test that the form is valid when no assignment is made"""
        form = EquipmentAssignmentForm(data={'assigned_unit': '', 'assigned_personnel': ''}, units=self.units)
        self.assertTrue(form.is_valid())


class SearchFormTest(TestCase):
    """Test the equipment search form functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.valid_data = {
            'query': 'M4A1',
            'category': 'weapons',
            'status': 'operational'
        }
    
    def test_valid_search_form(self):
        """Test form with valid data"""
        form = SearchForm(data=self.valid_data)
        self.assertTrue(form.is_valid())
    
    def test_empty_form_is_valid(self):
        """Test that an empty search form is valid"""
        form = SearchForm(data={})
        self.assertTrue(form.is_valid())
    
    def test_get_search_params(self):
        """Test that get_search_params method returns correct dictionary"""
        form = SearchForm(data=self.valid_data)
        self.assertTrue(form.is_valid())

        params = form.get_search_params()

        # Check that all valid fields are included
        self.assertEqual(params['query'], 'M4A1')
        self.assertEqual(params['category'], 'weapons')
        self.assertEqual(params['status'], 'operational')
    
    def test_get_search_params_empty(self):
        """Test that get_search_params handles empty form correctly"""
        form = SearchForm(data={})
        self.assertTrue(form.is_valid())

        params = form.get_search_params()
        self.assertEqual(params, {})
    
    def test_get_search_params_partial(self):
        """Test that get_search_params handles partial data correctly"""
        form = SearchForm(data={'query': 'M4A1', 'status': 'operational'})
        self.assertTrue(form.is_valid())

        params = form.get_search_params()
        self.assertEqual(params['query'], 'M4A1')
        self.assertEqual(params['status'], 'operational')
        self.assertNotIn('category', params)
