import requests
import json
from config import config
from typing import Dict, Optional, Tuple

class TikTokAuth:
    def __init__(self):
        self.access_token = None
        self.refresh_token = None
        
    def get_authorization_url(self) -> str:
        """Generate TikTok OAuth authorization URL"""
        params = {
            'client_key': config.CLIENT_ID,
            'redirect_uri': config.REDIRECT_URI,
            'response_type': 'code',
            'scope': 'ads.manage',
            'state': 'tiktok_auth_state'
        }
        
        # In a real implementation, this would construct the actual TikTok URL
        # For this assignment, we'll simulate the flow
        return f"{config.TIKTOK_OAUTH_URL}/authorize?{self._build_query_params(params)}"
    
    def handle_oauth_callback(self, auth_code: str) -> Tuple[bool, str]:
        """Exchange authorization code for access token"""
        try:
            # Mocked OAuth flow for assignment
            if auth_code == "valid_code":
                self.access_token = "mock_access_token_12345"
                self.refresh_token = "mock_refresh_token_67890"
                return True, "Authentication successful"
            elif auth_code == "invalid_client":
                return False, "Invalid client ID or secret. Please check your TikTok App credentials."
            elif auth_code == "no_permission":
                return False, "Missing Ads permission scope. Please ensure your TikTok App has ads.manage scope."
            else:
                return False, "Invalid authorization code"
                
        except Exception as e:
            return False, f"Authentication error: {str(e)}"
    
    def is_token_valid(self) -> bool:
        """Check if token is valid (mocked implementation)"""
        if not self.access_token:
            return False
            
        # Simulate token validation
        return self.access_token != "expired_token"
    
    def refresh_access_token(self) -> bool:
        """Refresh expired access token"""
        if not self.refresh_token:
            return False
            
        # Mock token refresh
        self.access_token = "refreshed_mock_token_12345"
        return True
    
    def _build_query_params(self, params: Dict) -> str:
        """Helper to build query parameter string"""
        return '&'.join([f"{k}={v}" for k, v in params.items()])
    
    def detect_oauth_error(self, error_response: Dict) -> Tuple[str, str]:
        """Interpret OAuth errors and provide user-friendly messages"""
        error_code = error_response.get('code', 'UNKNOWN_ERROR')
        
        error_mapping = {
            '40001': ('Invalid client credentials', 
                     'Please check your TikTok App Client ID and Secret'),
            '40002': ('Missing required permission scope',
                     'Ensure your TikTok App has ads.manage scope enabled'),
            '40003': ('Token expired or revoked',
                     'Please re-authenticate your account'),
            '40004': ('Geo-restriction applied',
                     'TikTok Ads API is not available in your region'),
            '40300': ('Insufficient permissions',
                     'Contact your TikTok Ads account administrator')
        }
        
        if error_code in error_mapping:
            return error_mapping[error_code]
        return ('Authentication failed', 'Please try re-authenticating')
