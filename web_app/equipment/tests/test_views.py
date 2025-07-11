"""
Tests for the Django views in the equipment app
"""
from unittest import mock
from django.test import TestCase, Client
from django.urls import reverse
from equipment.api import APIError


class DashboardViewTest(TestCase):
    """Test the dashboard view"""

    def setUp(self):
        self.client = Client()
        self.url = reverse('equipment:dashboard')
        self.stats_data = {
            "total_count": 100,
            "operational_count": 75,
            "maintenance_count": 15,
            "readiness_percentage": 75
        }
        self.maintenance_data = [
            {"equipment_id": "1", "maintenance_date": "2023-07-15", "equipment_name": "M4A1 Carbine"}
        ]
        self.equipment_list = [
            {"id": "1", "name": "M4A1 Carbine"},
            {"id": "2", "name": "M1A2 Abrams Tank"}
        ]

    @mock.patch('equipment.views.api_client')
    def test_dashboard_view_renders_successfully(self, mock_api_client):
        """Test that the dashboard renders with correct context"""
        mock_api_client.get_equipment_stats.return_value = self.stats_data
        mock_api_client.get_maintenance_equipment.return_value = {'data': self.maintenance_data}

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'equipment/dashboard.html')
        self.assertEqual(response.context['stats'], self.stats_data)
        self.assertEqual(response.context['maintenance_items'], self.maintenance_data)

    @mock.patch('equipment.views.api_client')
    def test_dashboard_handles_api_error(self, mock_api_client):
        """Test that dashboard handles API errors gracefully"""
        mock_api_client.get_equipment_stats.side_effect = APIError("API is down")

        response = self.client.get(self.url, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'equipment/dashboard.html')
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'API Error: API is down')


class EquipmentListViewTest(TestCase):
    """Test the equipment list view"""

    def setUp(self):
        self.client = Client()
        self.url = reverse('equipment:equipment_list')
        self.equipment_list = [
            {"id": "1", "name": "M4A1 Carbine"},
            {"id": "2", "name": "M1A2 Abrams Tank"}
        ]

    @mock.patch('equipment.views.api_client')
    def test_equipment_list_view(self, mock_api_client):
        """Test that the equipment list renders correctly"""
        mock_api_client.get_equipment_list.return_value = {'data': self.equipment_list, 'total': 2, 'page': 1, 'page_size': 20}

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'equipment/equipment_list.html')
        self.assertEqual(len(response.context['equipment_list']), 2)
        self.assertEqual(response.context['total_items'], 2)


class EquipmentSearchViewTest(TestCase):
    @mock.patch('equipment.views.api_client')
    def test_search_handles_api_error(self, mock_api_client):
        """Test that the search view handles API errors gracefully"""
        mock_api_client.search_equipment.side_effect = APIError("API is down")

        response = self.client.get(self.url, {'q': 'error'})

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'equipment/equipment_search.html')
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'API Error: API is down')
    """Test the equipment search view"""

    def setUp(self):
        self.client = Client()
        self.url = reverse('equipment:equipment_search')
        self.search_result = [
            {"id": "1", "name": "M4A1 Carbine"}
        ]

    @mock.patch('equipment.views.api_client')
    def test_equipment_search_view(self, mock_api_client):
        """Test that the search view renders and calls the correct API method"""
        mock_api_client.search_equipment.return_value = {'data': self.search_result}

        response = self.client.get(self.url, {'q': 'M4A1'})

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'equipment/equipment_search.html')
        mock_api_client.search_equipment.assert_called_once_with(query='M4A1', page=1)
        self.assertEqual(response.context['results']['data'], self.search_result)


class EquipmentDetailViewTest(TestCase):
    """Test the equipment detail view"""

    def setUp(self):
        self.client = Client()
        self.url = reverse('equipment:equipment_detail', kwargs={'equipment_id': 1})
        self.equipment_data = {"id": "1", "name": "M4A1 Carbine"}
        self.maintenance_logs = [{"description": "Routine check"}]

    @mock.patch('equipment.views.api_client')
    def test_equipment_detail_view(self, mock_api_client):
        """Test that the equipment detail view renders correctly"""
        mock_api_client.get_equipment.return_value = self.equipment_data
        mock_api_client.get_maintenance_logs.return_value = self.maintenance_logs

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'equipment/equipment_detail.html')
        self.assertEqual(response.context['equipment'], self.equipment_data)
        self.assertEqual(response.context['maintenance_logs'], self.maintenance_logs)


class MaintenanceListViewTest(TestCase):
    """Test the maintenance list view"""

    def setUp(self):
        self.client = Client()
        self.url = reverse('equipment:maintenance_list')
        self.maintenance_list = [{"id": "1", "equipment_name": "M4A1 Carbine"}]

    @mock.patch('equipment.views.api_client')
    def test_maintenance_list_view(self, mock_api_client):
        """Test that the maintenance list view renders correctly"""
        mock_api_client.get_maintenance_equipment.return_value = {'data': self.maintenance_list, 'total': 1, 'page': 1, 'page_size': 20}

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'equipment/maintenance_list.html')
        self.assertEqual(response.context['maintenance_schedule'], self.maintenance_list)


class ReportsDashboardViewTest(TestCase):
    """Test the reports dashboard view"""

    def setUp(self):
        self.client = Client()
        self.url = reverse('equipment:reports')
        self.stats_data = {"readiness_percentage": 75}

    @mock.patch('equipment.views.api_client')
    def test_reports_dashboard_view(self, mock_api_client):
        """Test that the reports dashboard view renders correctly"""
        mock_api_client.get_equipment_stats.return_value = self.stats_data

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'equipment/reports.html')
        self.assertEqual(response.context['stats'], self.stats_data)
