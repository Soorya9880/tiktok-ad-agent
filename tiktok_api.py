import requests
import json
import time
from typing import Dict, Tuple, Optional
from config import config
import string  

class TikTokAPI:
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = config.TIKTOK_API_BASE_URL
        
    def validate_music_id(self, music_id: str) -> Tuple[bool, str, Optional[Dict]]:
        """Validate if a music ID exists and is usable"""
        # Mock validation logic
        time.sleep(0.5)  # Simulate API delay
        
        if music_id in config.INVALID_MUSIC_IDS:
            return False, "MUSIC_NOT_FOUND", {
                "code": 40001,
                "message": "Music ID not found or not accessible",
                "log_id": "mock_log_123"
            }
        
        if music_id in config.MOCK_MUSIC_IDS:
            return True, "SUCCESS", {
                "music_id": music_id,
                "title": "Mock Music Track",
                "artist": "Mock Artist",
                "duration": 30,
                "is_usable": True
            }
        
        # Simulate random API failure (10% chance)
        import random
        if random.random() < 0.1:
            return False, "API_UNAVAILABLE", {
                "code": 50000,
                "message": "TikTok API service temporarily unavailable",
                "log_id": "mock_log_500"
            }
        
        return False, "INVALID_FORMAT", {
            "code": 40002,
            "message": "Invalid music ID format",
            "log_id": "mock_log_456"
        }
    
    def upload_custom_music(self, music_file_path: str) -> Tuple[bool, str, Optional[str]]:
        """Simulate custom music upload"""
        time.sleep(1.0)  # Simulate upload time
        
        # Mock upload - generate a mock music ID
        import random
        import string
        
        mock_id = "M" + ''.join(random.choices(string.digits, k=9))
        
        # Simulate 5% chance of upload failure
        if random.random() < 0.05:
            return False, "UPLOAD_FAILED", None
        
        return True, "UPLOAD_SUCCESS", mock_id
    
    def create_ad_campaign(self, ad_payload: Dict) -> Tuple[bool, Optional[Dict]]:
        """Submit ad campaign to TikTok API"""
        time.sleep(0.8)  # Simulate API delay
        
        # Mock various API failure scenarios
        import random
        scenario = random.random()
        
        # Scenario 1: Invalid OAuth token (15% chance)
        if scenario < 0.15:
            return False, {
                "code": 40003,
                "message": "Invalid OAuth token",
                "log_id": "mock_log_789",
                "request_id": "mock_req_123"
            }
        
        # Scenario 2: Missing permission (10% chance)
        elif scenario < 0.25:
            return False, {
                "code": 40002,
                "message": "Missing ads.manage permission",
                "log_id": "mock_log_101",
                "request_id": "mock_req_124"
            }
        
        # Scenario 3: Geo-restriction (5% chance)
        elif scenario < 0.30:
            return False, {
                "code": 40004,
                "message": "Service not available in your region",
                "log_id": "mock_log_102",
                "request_id": "mock_req_125"
            }
        
        # Scenario 4: Invalid music ID (10% chance)
        elif scenario < 0.40 and ad_payload.get('music_id'):
            return False, {
                "code": 40001,
                "message": "Invalid music ID",
                "log_id": "mock_log_103",
                "request_id": "mock_req_126"
            }
        
        # Scenario 5: Success (60% chance)
        else:
            return True, {
                "code": 0,
                "message": "SUCCESS",
                "data": {
                    "campaign_id": "CMP" + ''.join(random.choices(string.digits, k=10)),
                    "ad_id": "AD" + ''.join(random.choices(string.digits, k=10)),
                    "status": "UNDER_REVIEW",
                    "estimated_review_time": "24 hours"
                },
                "log_id": "mock_log_200",
                "request_id": "mock_req_200"
            }
    
    def interpret_api_error(self, error_response: Dict) -> Dict:
        """Interpret API errors for user-friendly messages"""
        error_code = error_response.get('code', 'UNKNOWN')
        
        interpretations = {
            '40001': {
                'explanation': 'The music ID you provided is invalid or not accessible.',
                'action': 'Please check the music ID or choose different music.',
                'can_retry': True,
                'retry_suggestion': 'Retry with a valid music ID after verification'
            },
            '40002': {
                'explanation': 'Your TikTok App does not have the required permissions.',
                'action': 'Contact your TikTok Ads administrator to grant ads.manage scope.',
                'can_retry': False,
                'retry_suggestion': 'Cannot retry until permissions are fixed'
            },
            '40003': {
                'explanation': 'Your access token has expired or is invalid.',
                'action': 'Please re-authenticate your TikTok Ads account.',
                'can_retry': True,
                'retry_suggestion': 'Retry after refreshing your access token'
            },
            '40004': {
                'explanation': 'TikTok Ads API is not available in your region.',
                'action': 'Use a VPN or contact TikTok support for regional access.',
                'can_retry': False,
                'retry_suggestion': 'Cannot retry from this geographic location'
            },
            '50000': {
                'explanation': 'TikTok Ads API is experiencing temporary issues.',
                'action': 'Please try again in a few minutes.',
                'can_retry': True,
                'retry_suggestion': 'Retry after 5-10 minutes'
            }
        }
        
        default_response = {
            'explanation': 'An unknown error occurred with the TikTok API.',
            'action': 'Please check your input and try again. Contact support if issue persists.',
            'can_retry': True,
            'retry_suggestion': 'Retry with the same parameters'
        }
        
        return interpretations.get(str(error_code), default_response)
