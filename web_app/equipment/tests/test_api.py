"""
Tests for the API client used to communicate with the FastAPI backend service
"""
import json
from unittest import mock
from django.test import TestCase
from django.conf import settings
from requests.exceptions import RequestException, Timeout, ConnectionError

from equipment.api import APIClient, APIError


class MockResponse:
    """Mock response class to simulate requests responses"""
    
    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code
        self.text = json.dumps(json_data)
        
    def json(self):
        return self.json_data
    
    def raise_for_status(self):
        if self.status_code >= 400:
            raise RequestException(f"HTTP Error: {self.status_code}")


class APIClientTestCase(TestCase):
    """Test cases for the Equipment API Client"""
    
    def setUp(self):
        """Set up test case with mock API client"""
        self.api_client = APIClient()
        self.api_url = settings.API_URL
        
        # Sample equipment data for testing
        self.sample_equipment = {
            "id": "1",
            "name": "M4A1 Carbine",
            "category": "weapons",
            "status": "operational",
            "location": "Alpha Base",
            "serial_number": "M4A1-12345-XYZ",
            "classification_level": "unclassified",
            "assigned_unit": "1st Infantry Division",
            "assigned_personnel": "Sergeant J. Smith",
            "purchase_date": "2023-01-15",
            "last_maintenance": "2023-05-20",
            "next_maintenance_due": "2023-08-20",
            "condition_rating": 4,
            "created_at": "2023-01-15T12:00:00Z",
            "updated_at": "2023-05-20T14:30:00Z"
        }
        
        self.equipment_list = [self.sample_equipment, {
            "id": "2",
            "name": "M1A2 Abrams Tank",
            "category": "vehicles",
            "status": "maintenance",
            "serial_number": "ABR-987654",
            "classification_level": "confidential",
        }]
        
        self.stats_data = {
            "total_count": 100,
            "operational_count": 75,
            "maintenance_count": 15,
            "damaged_count": 8,
            "decommissioned_count": 2,
            "readiness_percentage": 75,
            "category_counts": {
                "weapons": 40,
                "vehicles": 20,
                "communications": 15,
                "protective_gear": 10,
                "medical": 8,
                "electronics": 7
            },
            "classification_counts": {
                "unclassified": 60,
                "confidential": 30,
                "secret": 10
            }
        }
    
    @mock.patch('requests.Session.get')
    def test_get_equipment_list(self, mock_get):
        """Test getting a list of equipment"""
        # Configure mock to return a successful response
        mock_get.return_value = MockResponse({"data": self.equipment_list}, 200)
        
        # Call the method
        result = self.api_client.get_equipment_list()
        
        # Verify expected behavior
        mock_get.assert_called_once()
        self.assertEqual(mock_get.call_args.args[0], f"{self.api_url}/equipment")
        self.assertEqual(mock_get.call_args.kwargs['params'], {'skip': 0, 'limit': 10})
        self.assertEqual(result, {'data': self.equipment_list})
    
    @mock.patch('requests.Session.get')
    def test_get_equipment(self, mock_get):
        """Test getting equipment details"""
        # Configure mock
        mock_get.return_value = MockResponse({"data": self.sample_equipment}, 200)
        
        # Call the method
        result = self.api_client.get_equipment("1")
        
        # Verify expected behavior
        mock_get.assert_called_once()
        self.assertEqual(mock_get.call_args.args[0], f"{self.api_url}/equipment/1")
        self.assertEqual(result, {'data': self.sample_equipment})
    
    @mock.patch('requests.Session.post')
    def test_create_equipment(self, mock_post):
        """Test creating new equipment"""
        # Configure mock
        mock_post.return_value = MockResponse({"data": self.sample_equipment}, 201)
        
        # Call the method
        result = self.api_client.create_equipment(self.sample_equipment)
        
        # Verify expected behavior
        mock_post.assert_called_once()
        self.assertEqual(mock_post.call_args.kwargs['json'], self.sample_equipment)
        result_data = result['data']
        self.assertIn('id', result_data)
        self.assertIn('created_at', result_data)
        self.assertEqual(result_data['name'], self.sample_equipment['name'])
        self.assertEqual(result_data['category'], self.sample_equipment['category'])
        self.assertEqual(result_data['status'], self.sample_equipment['status'])
        self.assertEqual(result_data['location'], self.sample_equipment['location'])
        self.assertEqual(result_data['serial_number'], self.sample_equipment['serial_number'])
        self.assertEqual(result_data['classification_level'], self.sample_equipment['classification_level'])
        self.assertEqual(result_data['assigned_unit'], self.sample_equipment['assigned_unit'])
        self.assertEqual(result_data['assigned_personnel'], self.sample_equipment['assigned_personnel'])
        self.assertEqual(result_data['purchase_date'], self.sample_equipment['purchase_date'])
        self.assertEqual(result_data['last_maintenance'], self.sample_equipment['last_maintenance'])
        self.assertEqual(result_data['next_maintenance_due'], self.sample_equipment['next_maintenance_due'])
        self.assertEqual(result_data['condition_rating'], self.sample_equipment['condition_rating'])
    
    @mock.patch('requests.Session.put')
    def test_update_equipment(self, mock_put):
        """Test updating equipment"""
        # Configure mock
        updated_equipment = self.sample_equipment.copy()
        updated_equipment["status"] = "maintenance"
        mock_put.return_value = MockResponse({"data": updated_equipment}, 200)
        
        # Call the method
        result = self.api_client.update_equipment("1", updated_equipment)
        
        # Verify expected behavior
        mock_put.assert_called_once()
        self.assertEqual(mock_put.call_args.kwargs['json'], updated_equipment)
        # Check that the result contains the updated data
        for key, value in updated_equipment.items():
            self.assertEqual(result['data'][key], value)
    
    @mock.patch('requests.Session.delete')
    def test_delete_equipment(self, mock_delete):
        """Test deleting equipment"""
        # Configure mock
        mock_delete.return_value = MockResponse({"success": True}, 204)
        
        # Call the method
        result = self.api_client.delete_equipment("1")
        
        # Verify expected behavior
        mock_delete.assert_called_once()
        self.assertEqual(mock_delete.call_args.args[0], f"{self.api_url}/equipment/1")
        self.assertTrue(result)
    
    @mock.patch('requests.Session.get')
    def test_search_equipment(self, mock_get):
        """Test searching for equipment"""
        # Configure mock
        mock_get.return_value = MockResponse({"data": [self.sample_equipment]}, 200)
        
        # Call the method
        search_params = {"query": "M4", "category": "weapons"}
        result = self.api_client.search_equipment(**search_params)
        
        # Verify expected behavior
        expected_params = {'skip': 0, 'limit': 10, **search_params}
        mock_get.assert_called_once()
        self.assertEqual(mock_get.call_args.kwargs['params'], expected_params)
        self.assertEqual(result, {'data': [self.sample_equipment]})
    
    @mock.patch('requests.Session.get')
    def test_get_equipment_stats(self, mock_get):
        """Test getting equipment statistics"""
        # Configure mock
        mock_get.return_value = MockResponse({"data": self.stats_data}, 200)
        
        # Call the method
        result = self.api_client.get_equipment_stats()
        
        # Verify expected behavior
        mock_get.assert_called_once()
        self.assertEqual(mock_get.call_args.args[0], f"{self.api_url}/equipment/stats")
        self.assertEqual(result, {'data': self.stats_data})
    
    @mock.patch('requests.Session.get')
    def test_get_equipment_by_unit(self, mock_get):
        """Test getting equipment assigned to a unit"""
        # Configure mock
        mock_get.return_value = MockResponse({"data": [self.sample_equipment]}, 200)
        
        # Call the method
        result = self.api_client.get_equipment_by_unit("1st Infantry Division")
        
        # Verify expected behavior
        mock_get.assert_called_once()
        self.assertEqual(mock_get.call_args.args[0], f"{self.api_url}/equipment/unit/1st Infantry Division")
        self.assertEqual(mock_get.call_args.kwargs['params'], {'skip': 0, 'limit': 10})
        self.assertEqual(result, {'data': [self.sample_equipment]})
    
    @mock.patch('requests.Session.get')
    def test_get_maintenance_equipment(self, mock_get):
        """Test getting maintenance equipment"""
        maintenance_data = [
            {
                "id": "1",
                "equipment_id": "1",
                "maintenance_date": "2023-05-20",
                "performed_by": "Tech Sergeant Williams",
                "maintenance_type": "routine",
                "notes": "Regular maintenance completed"
            }
        ]
        # Configure mock
        mock_get.return_value = MockResponse({"data": maintenance_data}, 200)
        
        # Call the method
        result = self.api_client.get_maintenance_equipment()
        
        # Verify expected behavior
        mock_get.assert_called_once()
        self.assertEqual(mock_get.call_args.args[0], f"{self.api_url}/equipment/maintenance")
        self.assertEqual(mock_get.call_args.kwargs['params'], {'skip': 0, 'limit': 10})
        self.assertEqual(result, {'data': maintenance_data})
    
    @mock.patch('requests.Session.get')
    def test_api_error_handling(self, mock_get):
        """Test error handling when API returns error"""
        # Configure mock to return an error
        mock_get.return_value = MockResponse({"detail": "Not found"}, 404)
        
        # Call the method and check exception handling
        with self.assertRaises(APIError):
            self.api_client.get_equipment("999")
    
    @mock.patch('requests.Session.get')
    def test_api_timeout_handling(self, mock_get):
        """Test handling of API timeout"""
        # Configure mock to raise Timeout
        mock_get.side_effect = Timeout("Request timed out")
        
        # Call the method and check exception handling
        with self.assertRaises(APIError):
            self.api_client.get_equipment_list()
    
    @mock.patch('requests.Session.get')
    def test_api_connection_error_handling(self, mock_get):
        """Test handling of API connection error"""
        # Configure mock to raise ConnectionError
        mock_get.side_effect = ConnectionError("Connection failed")
        
        # Call the method and check exception handling
        with self.assertRaises(APIError):
            self.api_client.get_equipment_stats()
