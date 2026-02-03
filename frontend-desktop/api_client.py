"""
API Client for Desktop Application

Handles all API communication with the Django backend
"""
import requests
from typing import Dict, List, Optional, Any


class APIClient:
    """Client for communicating with the backend API"""
    
    def __init__(self, base_url: str = "http://localhost:8000/api/v1"):
        self.base_url = base_url
        self.token: Optional[str] = None
        self.session = requests.Session()
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers with auth token if available"""
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Token {self.token}"
        return headers
    
    # Authentication
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """Login and get authentication token"""
        response = self.session.post(
            f"{self.base_url}/auth/login/",
            json={"username": username, "password": password}
        )
        response.raise_for_status()
        data = response.json()
        self.token = data["token"]
        return data
    
    def register(self, username: str, password: str, email: str) -> Dict[str, Any]:
        """Register a new user"""
        response = self.session.post(
            f"{self.base_url}/auth/register/",
            json={"username": username, "password": password, "email": email}
        )
        response.raise_for_status()
        data = response.json()
        self.token = data["token"]
        return data
    
    # Datasets
    def list_datasets(self) -> List[Dict[str, Any]]:
        """Get list of user's datasets"""
        response = self.session.get(
            f"{self.base_url}/datasets/",
            headers=self._get_headers()
        )
        response.raise_for_status()
        data = response.json()
        # Handle paginated response from DRF
        return data.get('results', data) if isinstance(data, dict) else data
    
    def upload_dataset(self, file_path: str) -> Dict[str, Any]:
        """Upload a CSV file"""
        headers = {}
        if self.token:
            headers["Authorization"] = f"Token {self.token}"
        
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = self.session.post(
                f"{self.base_url}/datasets/upload/",
                files=files,
                headers=headers
            )
        
        response.raise_for_status()
        return response.json()
    
    def get_analytics(self, dataset_id: int) -> Dict[str, Any]:
        """Get analytics for a dataset"""
        response = self.session.get(
            f"{self.base_url}/datasets/{dataset_id}/analytics/",
            headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    def download_report(self, dataset_id: int, save_path: str):
        """Download PDF report"""
        response = self.session.get(
            f"{self.base_url}/datasets/{dataset_id}/report/",
            headers=self._get_headers(),
            stream=True
        )
        response.raise_for_status()
        
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
