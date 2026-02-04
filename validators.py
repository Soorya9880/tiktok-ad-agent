from typing import Dict, Tuple, Optional
from config import config

class AdValidator:
    @staticmethod
    def validate_campaign_name(name: str) -> Tuple[bool, str]:
        if not name or len(name.strip()) < config.MIN_CAMPAIGN_NAME_LENGTH:
            return False, f"Campaign name must be at least {config.MIN_CAMPAIGN_NAME_LENGTH} characters"
        return True, "Valid campaign name"
    
    @staticmethod
    def validate_objective(objective: str) -> Tuple[bool, str]:
        if objective.upper() not in config.ALLOWED_OBJECTIVES:
            return False, f"Objective must be one of: {', '.join(config.ALLOWED_OBJECTIVES)}"
        return True, "Valid objective"
    
    @staticmethod
    def validate_ad_text(text: str) -> Tuple[bool, str]:
        if not text:
            return False, "Ad text is required"
        if len(text) > config.MAX_AD_TEXT_LENGTH:
            return False, f"Ad text must be {config.MAX_AD_TEXT_LENGTH} characters or less"
        return True, "Valid ad text"
    
    @staticmethod
    def validate_music_logic(objective: str, music_option: str, music_id: Optional[str] = None) -> Tuple[bool, str]:
        """Validate music selection based on business rules"""
        
        # Case C: No music
        if music_option.upper() == "NO_MUSIC":
            if objective.upper() == "CONVERSIONS":
                return False, "Music is required for Conversions objective"
            elif objective.upper() == "TRAFFIC":
                return True, "No music selected (allowed for Traffic)"
        
        # Case A: Existing Music ID
        elif music_option.upper() == "EXISTING":
            if not music_id:
                return False, "Music ID is required for existing music"
            # Additional validation would happen in API call
            return True, "Existing music ID provided"
        
        # Case B: Custom music
        elif music_option.upper() == "CUSTOM":
            return True, "Custom music upload requested"
        
        return False, "Invalid music option"
    
    @staticmethod
    def validate_all_fields(ad_data: Dict) -> Tuple[bool, Dict[str, str]]:
        """Validate all ad fields and return detailed errors"""
        errors = {}
        
        # Campaign Name
        is_valid, message = AdValidator.validate_campaign_name(ad_data.get('campaign_name', ''))
        if not is_valid:
            errors['campaign_name'] = message
        
        # Objective
        is_valid, message = AdValidator.validate_objective(ad_data.get('objective', ''))
        if not is_valid:
            errors['objective'] = message
        
        # Ad Text
        is_valid, message = AdValidator.validate_ad_text(ad_data.get('ad_text', ''))
        if not is_valid:
            errors['ad_text'] = message
        
        # Music Logic
        is_valid, message = AdValidator.validate_music_logic(
            ad_data.get('objective', ''),
            ad_data.get('music_option', ''),
            ad_data.get('music_id')
        )
        if not is_valid:
            errors['music_logic'] = message
        
        return len(errors) == 0, errors
