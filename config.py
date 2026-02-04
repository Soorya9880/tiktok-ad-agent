import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # NVIDIA NIM Configuration (OpenAI-compatible)
    NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
    NVIDIA_BASE_URL = os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1")
    
    # Available NVIDIA models (free tier):
    # - "nvidia/nemotron-3-nano-30b-a3b" (your example)
    # - "meta/llama-3.1-8b-instruct"
    # - "mistralai/mistral-7b-instruct"
    # - "microsoft/phi-3-mini-4k-instruct"
    NVIDIA_MODEL = os.getenv("NVIDIA_MODEL", "meta/llama-3.1-8b-instruct")
    
    # TikTok API Configuration (Mocked for this assignment)
    TIKTOK_API_BASE_URL = "https://ads.tiktok.com/open_api/v1.3"
    TIKTOK_OAUTH_URL = "https://ads.tiktok.com/marketing_api/auth"
    
    # App Configuration
    CLIENT_ID = os.getenv("TIKTOK_CLIENT_ID", "mock_client_id")
    CLIENT_SECRET = os.getenv("TIKTOK_CLIENT_SECRET", "mock_client_secret")
    REDIRECT_URI = "http://localhost:8000/callback"
    
    # Business Rules
    MIN_CAMPAIGN_NAME_LENGTH = 3
    MAX_AD_TEXT_LENGTH = 100
    ALLOWED_OBJECTIVES = ["TRAFFIC", "CONVERSIONS"]
    
    # Mock API Responses
    MOCK_MUSIC_IDS = ["M123456789", "M987654321", "M555555555"]
    INVALID_MUSIC_IDS = ["M000000000", "M999999999"]
    
    # LLM Settings
    LLM_TEMPERATURE = 0.3
    LLM_MAX_TOKENS = 1024
    
config = Config()
