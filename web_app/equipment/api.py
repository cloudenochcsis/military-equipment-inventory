"""
API client for communicating with the FastAPI service
"""
import requests
import logging
import json
from typing import Dict, List, Any, Optional
from datetime import date, datetime
from django.conf import settings

logger = logging.getLogger(__name__)

class APIClient:
    """Client for communicating with the Equipment API"""
    
    def __init__(self):
        self.base_url = settings.API_URL
        self.session = requests.Session()
    
    def _make_request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None) -> Dict:
        """Make HTTP request to API with error handling"""
        url = f"{self.base_url}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        try:
            if method.lower() == "get":
                response = self.session.get(url, headers=headers, params=params)
            elif method.lower() == "post":
                response = self.session.post(url, headers=headers, json=data)
            elif method.lower() == "put":
                response = self.session.put(url, headers=headers, json=data)
            elif method.lower() == "delete":
                response = self.session.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            # Log the request details
            logger.info(f"API Request: {method} {url} - Status: {response.status_code}")
            
            # Check for success
            response.raise_for_status()
            
            # Return JSON response if content exists, otherwise empty dict
            return response.json() if response.text else {}
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API Error: {method} {url} - {str(e)}")
            try:
                error_message = response.json().get("detail", str(e)) if response else str(e)
            except:
                error_message = str(e)
                
            raise APIError(error_message)
    
    # Equipment endpoints
    def get_equipment_list(self, page: int = 1, page_size: int = 10, **filters) -> Dict:
        """Get paginated list of equipment with filters"""
        params = {
            "skip": (page - 1) * page_size, 
            "limit": page_size,
            **{k: v for k, v in filters.items() if v}
        }
        return self._make_request("GET", "/equipment", params=params)
    
    def get_equipment(self, equipment_id: int) -> Dict:
        """Get equipment details by ID"""
        return self._make_request("GET", f"/equipment/{equipment_id}")
    
    def create_equipment(self, data: Dict) -> Dict:
        """Create new equipment"""
        # Prepare data for API (handles dates and enum values)
        prepared_data = self._prepare_equipment_data(data)
        return self._make_request("POST", "/equipment", data=prepared_data)
    
    def update_equipment(self, equipment_id: int, data: Dict) -> Dict:
        """Update equipment details"""
        # Prepare data for API (handles dates and enum values)
        prepared_data = self._prepare_equipment_data(data)
        return self._make_request("PUT", f"/equipment/{equipment_id}", data=prepared_data)
    
    def delete_equipment(self, equipment_id: int) -> None:
        """Delete equipment"""
        return self._make_request("DELETE", f"/equipment/{equipment_id}")
    
    def search_equipment(self, page: int = 1, page_size: int = 10, **filters) -> List:
        """Search equipment by term"""
        params = {
            "skip": (page - 1) * page_size, 
            "limit": page_size,
            **{k: v for k, v in filters.items() if v}
        }
        return self._make_request("GET", "/equipment/search", params=params)
    
    def get_equipment_stats(self) -> Dict:
        """Get equipment statistics"""
        return self._make_request("GET", "/equipment/stats")
    
    def get_maintenance_equipment(self, page: int = 1, page_size: int = 10) -> List:
        """Get equipment due for maintenance"""
        params = {"skip": (page - 1) * page_size, "limit": page_size}
        return self._make_request("GET", "/equipment/maintenance", params=params)
    
    def get_units(self) -> List[str]:
        """Get a list of all distinct units."""
        return self._make_request("GET", "/units")

    def get_equipment_by_unit(self, unit_id: str, page: int = 1, page_size: int = 10) -> List:
        """Get equipment by assigned unit"""
        params = {"skip": (page - 1) * page_size, "limit": page_size}
        return self._make_request("GET", f"/equipment/unit/{unit_id}", params=params)
    
    def assign_equipment(self, equipment_id: int, unit: Optional[str], personnel: Optional[str]) -> Dict:
        """Assign equipment to unit or personnel"""
        data = {"assigned_unit": unit, "assigned_personnel": personnel}
        return self._make_request("POST", f"/equipment/{equipment_id}/assign", data=data)
        
    def _serialize_dates(self, data: Dict) -> Dict:
        """Convert date objects to ISO format strings for JSON serialization"""
        if not data:
            return data
            
        serialized_data = {}
        for key, value in data.items():
            if isinstance(value, (date, datetime)):
                serialized_data[key] = value.isoformat()
            else:
                serialized_data[key] = value
        return serialized_data
        
    def _prepare_equipment_data(self, data: Dict) -> Dict:
        """Prepare equipment data for API by handling dates and enum values
        
        The API expects enum values for category, status, and classification_level.
        This function ensures these fields are properly formatted.
        """
        # First serialize any date objects
        prepared_data = self._serialize_dates(data)
        
        # Ensure enum values are properly formatted
        # The API expects string values that match the enum values defined in schemas.py
        
        # For category, there's a special case with protective-gear
        # Django form uses 'protective-gear' but FastAPI enum member is protective_gear (with underscore)
        # However, the actual enum value is still 'protective-gear' (with hyphen)
        # So we don't need to change anything for this field
        
        # For status and classification_level, the values match between Django and FastAPI
        # So we don't need to change anything for these fields either
        
        # Log the data being sent to the API for debugging
        logger.info(f"Prepared equipment data for API: {prepared_data}")
        
        return prepared_data
    
    def get_maintenance_logs(self, equipment_id: int) -> List:
        """Get maintenance logs for equipment"""
        return self._make_request("GET", f"/maintenance/{equipment_id}")
    
    def create_maintenance_log(self, data: Dict) -> Dict:
        """Create maintenance log entry"""
        # Serialize any date objects to ISO format strings
        serialized_data = self._serialize_dates(data)
        return self._make_request("POST", "/maintenance", data=serialized_data)


class APIError(Exception):
    """Custom exception for API errors"""
    pass


# Initialize API client (singleton)
api_client = APIClient()
