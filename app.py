import json
import sys
from typing import Dict
from colorama import init, Fore, Style
from config import config
from auth import TikTokAuth
from tiktok_api import TikTokAPI
from validators import AdValidator
from prompts import PromptTemplates
from nvidia_client import NVIDIAAIClient

init(autoreset=True)

class TikTokAdAgent:
    def __init__(self):
        # Initialize NVIDIA OpenAI client
        self.client = NVIDIAAIClient()
        self.auth = TikTokAuth()
        self.api = None
        print(Fore.CYAN + f"Using NVIDIA Model: {config.NVIDIA_MODEL}")
        
    def initialize_authentication(self):
        """Handle OAuth2 authentication flow"""
        print(Fore.CYAN + "\n" + "="*50)
        print(Fore.CYAN + "TikTok Ads Authentication")
        print(Fore.CYAN + "="*50)
        
        print("\n1. Redirecting to TikTok for authentication...")
        auth_url = self.auth.get_authorization_url()
        print(f"   Auth URL: {auth_url}")
        
        print("\n2. Please enter the authorization code from the callback URL:")
        print("   (Use 'valid_code' for success, 'invalid_client' for error, 'no_permission' for scope error)")
        
        auth_code = input(Fore.YELLOW + "   Authorization code: " + Style.RESET_ALL).strip()
        
        success, message = self.auth.handle_oauth_callback(auth_code)
        
        if success:
            print(Fore.GREEN + f"\n✓ {message}")
            self.api = TikTokAPI(self.auth.access_token)
            return True
        else:
            print(Fore.RED + f"\n✗ {message}")
            
            if "Invalid client" in message:
                print(Fore.YELLOW + "   Action: Check your TikTok Developer App credentials")
            elif "Missing Ads permission" in message:
                print(Fore.YELLOW + "   Action: Enable ads.manage scope in your TikTok App")
            elif "Invalid authorization" in message:
                print(Fore.YELLOW + "   Action: Try the authentication process again")
                
            return False
    
     # Update the get_llm_response method in app.py
    def get_llm_response(self, user_input: str, collected_data: Dict) -> Dict:
        """Get structured response from NVIDIA LLM"""
        # Build conversation context
        context = f"Current collected data: {json.dumps(collected_data, indent=2)}"
        
        # For first message, use the structured CONVERSATION_START
        if not any(collected_data.values()) and user_input == "":
            return PromptTemplates.CONVERSATION_START
        
        user_prompt = f"{context}\n\nUser says: {user_input}"
        
        try:
            response_text = self.client.chat_completion(
                messages=[
                    {"role": "system", "content": PromptTemplates.SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            # Parse JSON response
            try:
                response_data = json.loads(response_text)
                
                # Validate the response has required fields
                required_fields = ["user_message", "internal_reasoning", "collected_data", "next_step"]
                if not all(field in response_data for field in required_fields):
                    raise json.JSONDecodeError("Missing required fields", "", 0)
                
                return response_data
                
            except json.JSONDecodeError as e:
                print(Fore.YELLOW + f"Warning: LLM returned invalid JSON, attempting to fix...")
                print(Fore.YELLOW + f"Raw response: {response_text[:200]}...")
                
                # Try to extract JSON from text
                import re
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    try:
                        response_data = json.loads(json_match.group())
                        if all(field in response_data for field in required_fields):
                            return response_data
                    except:
                        pass
                
                # Fallback to rule-based response
                return self._get_fallback_response(user_input, collected_data)
                
        except Exception as e:
            print(Fore.RED + f"LLM Error: {str(e)}")
            return self._get_fallback_response(user_input, collected_data)

    def _get_fallback_response(self, user_input: str, collected_data: Dict) -> Dict:
        """Fallback response when LLM fails"""
        # Simple rule-based fallback
        if not collected_data.get("campaign_name"):
            return {
                "user_message": "Let's start with your campaign name. What would you like to name it?",
                "internal_reasoning": "Fallback: Asking for campaign name",
                "collected_data": {"campaign_name": user_input} if user_input else collected_data,
                "next_step": "campaign_name" if not user_input else "objective"
            }
        elif not collected_data.get("objective"):
            return {
                "user_message": "Great! Now what's your campaign objective? (Choose: TRAFFIC or CONVERSIONS)",
                "internal_reasoning": f"Fallback: User provided campaign name '{user_input if user_input else collected_data.get('campaign_name')}'. Need objective.",
                "collected_data": {**collected_data, "objective": user_input.upper() if user_input else ""},
                "next_step": "objective" if not user_input else "ad_text"
            }
        elif not collected_data.get("ad_text"):
            return {
                "user_message": f"Objective set. Now please write your ad text (max 100 characters):",
                "internal_reasoning": f"Fallback: Objective collected. Need ad text.",
                "collected_data": {**collected_data, "ad_text": user_input if user_input else ""},
                "next_step": "ad_text" if not user_input else "cta"
            }
        elif not collected_data.get("cta"):
            return {
                "user_message": "Now what call-to-action would you like? (e.g., 'Shop Now', 'Learn More', 'Sign Up'):",
                "internal_reasoning": "Fallback: Ad text collected. Need CTA.",
                "collected_data": {**collected_data, "cta": user_input if user_input else ""},
                "next_step": "cta" if not user_input else "music"
            }
        elif not collected_data.get("music_option"):
            # Determine if music is required
            objective = collected_data.get("objective", "").upper()
            if objective == "CONVERSIONS":
                return {
                    "user_message": "For CONVERSIONS objective, music is required. Choose: 1) Use existing TikTok music, 2) Upload custom music",
                    "internal_reasoning": "Fallback: Music required for CONVERSIONS. Need music option.",
                    "collected_data": collected_data,
                    "next_step": "music"
                }
            else:
                return {
                    "user_message": "For music, choose: 1) Use existing TikTok music, 2) Upload custom music, 3) No music",
                    "internal_reasoning": "Fallback: Music optional for TRAFFIC. Need music option.",
                    "collected_data": collected_data,
                    "next_step": "music"
                }
        else:
            # All fields collected, ready for validation
            return {
                "user_message": "Perfect! I have all the information. Let me validate everything.",
                "internal_reasoning": "Fallback: All fields collected. Ready for validation.",
                "collected_data": collected_data,
                "next_step": "validation"
            }
        
    def collect_ad_inputs(self) -> Dict:
        """Guide user through conversational ad creation"""
        print(Fore.CYAN + "\n" + "="*50)
        print(Fore.CYAN + "TikTok Ad Creation")
        print(Fore.CYAN + "="*50)
        
        collected_data = {
            "campaign_name": "",
            "objective": "",
            "ad_text": "",
            "cta": "",
            "music_option": "",
            "music_id": ""
        }
        
        print(Fore.GREEN + "\n" + PromptTemplates.CONVERSATION_START["user_message"])
        
        while True:
            user_input = input(Fore.YELLOW + "\nYou: " + Style.RESET_ALL).strip()
            
            if user_input.lower() in ['quit', 'exit', 'cancel']:
                print(Fore.YELLOW + "Ad creation cancelled.")
                return None
            
            # Get structured response from LLM
            llm_response = self.get_llm_response(user_input, collected_data)
            
            # Update collected data
            if llm_response.get("collected_data"):
                collected_data.update(llm_response["collected_data"])
            
            # Print agent response
            print(Fore.BLUE + f"\nAssistant: {llm_response.get('user_message', '')}")
            
            # Handle special cases
            next_step = llm_response.get("next_step", "").lower()
            
            if next_step == "validation":
                return self.validate_and_process(collected_data)
            elif next_step == "ask_music_id":
                self.handle_music_id_input(collected_data)
            elif next_step == "ask_custom_music":
                self.handle_custom_music(collected_data)
            
            # Show current progress
            self.show_progress(collected_data)
    
    def handle_music_id_input(self, collected_data: Dict):
        """Handle existing music ID validation"""
        print(Fore.CYAN + "\nPlease enter the TikTok Music ID:")
        music_id = input(Fore.YELLOW + "Music ID: " + Style.RESET_ALL).strip()
        
        if music_id:
            print(Fore.BLUE + "\nValidating music ID with TikTok API...")
            is_valid, status, details = self.api.validate_music_id(music_id)
            
            if is_valid:
                print(Fore.GREEN + f"✓ Music ID validated: {details.get('title', 'Unknown Track')}")
                collected_data['music_id'] = music_id
                collected_data['music_option'] = 'EXISTING'
            else:
                print(Fore.RED + f"✗ Music validation failed: {status}")
                print(Fore.YELLOW + f"   Details: {details.get('message', 'Unknown error')}")
                
                print(Fore.CYAN + "\nWhat would you like to do?")
                print("1. Try a different Music ID")
                print("2. Upload custom music")
                print("3. Skip music (if allowed)")
                
                choice = input(Fore.YELLOW + "Choice (1-3): " + Style.RESET_ALL).strip()
                
                if choice == "1":
                    self.handle_music_id_input(collected_data)
                elif choice == "2":
                    self.handle_custom_music(collected_data)
                elif choice == "3":
                    is_allowed, message = AdValidator.validate_music_logic(
                        collected_data.get('objective', ''),
                        'NO_MUSIC'
                    )
                    if is_allowed:
                        collected_data['music_option'] = 'NO_MUSIC'
                        print(Fore.GREEN + "✓ Music skipped (allowed for Traffic objective)")
                    else:
                        print(Fore.RED + f"✗ Cannot skip music: {message}")
                        self.handle_music_id_input(collected_data)
    
    def handle_custom_music(self, collected_data: Dict):
        """Handle custom music upload"""
        print(Fore.CYAN + "\nCustom Music Upload")
        print("For this demo, we'll simulate the upload process.")
        
        confirm = input(Fore.YELLOW + "Upload custom music file? (yes/no): " + Style.RESET_ALL).strip().lower()
        
        if confirm == 'yes':
            file_path = input(Fore.YELLOW + "Enter music file path (simulated): " + Style.RESET_ALL).strip()
            
            print(Fore.BLUE + "\nUploading music to TikTok...")
            success, status, music_id = self.api.upload_custom_music(file_path)
            
            if success and music_id:
                print(Fore.GREEN + f"✓ Music uploaded successfully! Music ID: {music_id}")
                collected_data['music_id'] = music_id
                collected_data['music_option'] = 'CUSTOM'
            else:
                print(Fore.RED + f"✗ Upload failed: {status}")
                
                print(Fore.CYAN + "\nOptions:")
                print("1. Try uploading again")
                print("2. Use existing music instead")
                print("3. Skip music (if allowed)")
                
                choice = input(Fore.YELLOW + "Choice (1-3): " + Style.RESET_ALL).strip()
                
                if choice == "1":
                    self.handle_custom_music(collected_data)
                elif choice == "2":
                    self.handle_music_id_input(collected_data)
                elif choice == "3":
                    is_allowed, message = AdValidator.validate_music_logic(
                        collected_data.get('objective', ''),
                        'NO_MUSIC'
                    )
                    if is_allowed:
                        collected_data['music_option'] = 'NO_MUSIC'
                        print(Fore.GREEN + "✓ Proceeding without music")
                    else:
                        print(Fore.RED + f"✗ Cannot proceed: {message}")
                        self.handle_custom_music(collected_data)
        else:
            print(Fore.BLUE + "\nLet's explore other music options...")
            self.handle_music_id_input(collected_data)
    
    def validate_and_process(self, collected_data: Dict) -> Dict:
        """Validate collected data and prepare for submission"""
        print(Fore.CYAN + "\n" + "="*50)
        print(Fore.CYAN + "Validation & Submission")
        print(Fore.CYAN + "="*50)
        
        is_valid, errors = AdValidator.validate_all_fields(collected_data)
        
        if not is_valid:
            print(Fore.RED + "\n✗ Validation Errors Found:")
            for field, error in errors.items():
                print(Fore.RED + f"   • {field}: {error}")
            
            print(Fore.YELLOW + "\nPlease correct the errors above.")
            return None
        
        print(Fore.GREEN + "\n✓ All validations passed!")
        
        print(Fore.CYAN + "\nFinal Ad Configuration:")
        print(Fore.CYAN + "-" * 30)
        for key, value in collected_data.items():
            if value:
                print(f"{key.replace('_', ' ').title()}: {value}")
        
        print(Fore.CYAN + "\n" + "-" * 30)
        confirm = input(Fore.YELLOW + "Submit this ad campaign? (yes/no): " + Style.RESET_ALL).strip().lower()
        
        if confirm == 'yes':
            return collected_data
        else:
            print(Fore.YELLOW + "Submission cancelled.")
            return None
    
    def submit_ad_campaign(self, ad_payload: Dict):
        """Submit ad campaign and handle API responses"""
        print(Fore.BLUE + "\nSubmitting ad campaign to TikTok API...")
        
        success, response = self.api.create_ad_campaign(ad_payload)
        
        if success:
            print(Fore.GREEN + "\n✓ Ad campaign submitted successfully!")
            print(Fore.GREEN + f"   Campaign ID: {response['data']['campaign_id']}")
            print(Fore.GREEN + f"   Status: {response['data']['status']}")
            print(Fore.GREEN + f"   Estimated Review: {response['data']['estimated_review_time']}")
        else:
            print(Fore.RED + "\n✗ Submission failed!")
            
            error_interpretation = self.api.interpret_api_error(response)
            
            print(Fore.YELLOW + f"\nError Analysis:")
            print(Fore.YELLOW + f"   • What happened: {error_interpretation['explanation']}")
            print(Fore.YELLOW + f"   • Action needed: {error_interpretation['action']}")
            
            if error_interpretation['can_retry']:
                print(Fore.YELLOW + f"   • Retry suggestion: {error_interpretation['retry_suggestion']}")
                
                retry = input(Fore.YELLOW + "\nRetry submission? (yes/no): " + Style.RESET_ALL).strip().lower()
                if retry == 'yes':
                    if response.get('code') == 40003:
                        print(Fore.BLUE + "\nRefreshing access token...")
                        if self.auth.refresh_access_token():
                            self.api = TikTokAPI(self.auth.access_token)
                            print(Fore.GREEN + "✓ Token refreshed, retrying...")
                            self.submit_ad_campaign(ad_payload)
                        else:
                            print(Fore.RED + "✗ Token refresh failed. Please re-authenticate.")
                    else:
                        self.submit_ad_campaign(ad_payload)
            else:
                print(Fore.RED + "\n❌ This error cannot be retried automatically.")
                print(Fore.RED + "   Please fix the issue and try creating a new campaign.")
    
    def show_progress(self, collected_data: Dict):
        """Show current progress in data collection"""
        completed = sum(1 for v in collected_data.values() if v)
        total = len(collected_data)
        
        print(Fore.MAGENTA + f"\n[Progress: {completed}/{total} fields collected]")
        
        missing = [k.replace('_', ' ').title() for k, v in collected_data.items() if not v]
        if missing:
            print(Fore.MAGENTA + f"  Still needed: {', '.join(missing)}")
    
    def run(self):
        """Main execution flow"""
        print(Fore.CYAN + "="*60)
        print(Fore.CYAN + f"TikTok AI Ad Creation Agent")
        print(Fore.CYAN + f"Powered by NVIDIA {config.NVIDIA_MODEL}")
        print(Fore.CYAN + "="*60)
        
        if not self.initialize_authentication():
            print(Fore.RED + "\nAuthentication failed. Exiting...")
            return
        
        ad_payload = self.collect_ad_inputs()
        
        if not ad_payload:
            print(Fore.YELLOW + "\nAd creation incomplete. Exiting...")
            return
        
        self.submit_ad_campaign(ad_payload)
        
        print(Fore.CYAN + "\n" + "="*60)
        print(Fore.CYAN + "Process Complete!")
        print(Fore.CYAN + "="*60)

if __name__ == "__main__":
    try:
        agent = TikTokAdAgent()
        agent.run()
    except KeyboardInterrupt:
        print(Fore.YELLOW + "\n\nProcess interrupted by user. Exiting...")
        sys.exit(0)
    except Exception as e:
        print(Fore.RED + f"\nUnexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
