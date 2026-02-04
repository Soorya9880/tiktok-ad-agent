from openai import OpenAI
import json
from config import config

class NVIDIAAIClient:
    def __init__(self):
        self.client = OpenAI(
            base_url=config.NVIDIA_BASE_URL,
            api_key=config.NVIDIA_API_KEY
        )
        self.model = config.NVIDIA_MODEL
        
    def chat_completion(self, messages: list, temperature: float = None, max_tokens: int = None) -> dict:
        """Call NVIDIA NIM API using OpenAI-compatible interface"""
        
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature or config.LLM_TEMPERATURE,
                max_tokens=max_tokens or config.LLM_MAX_TOKENS,
                response_format={"type": "json_object"}  # Force JSON output
            )
            
            return completion.choices[0].message.content
            
        except Exception as e:
            print(f"NVIDIA API Error: {e}")
            raise
    
    def create_structured_response(self, system_prompt: str, user_prompt: str) -> dict:
        """Get structured JSON response from NVIDIA LLM"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            response_text = self.chat_completion(messages)
            
            # Parse JSON response
            try:
                return json.loads(response_text)
            except json.JSONDecodeError as e:
                print(f"JSON Parse Error: {e}")
                print(f"Raw response: {response_text[:200]}...")
                
                # Try to extract JSON from text if it's wrapped
                import re
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    try:
                        return json.loads(json_match.group())
                    except:
                        pass
                
                # Fallback response
                return {
                    "user_message": "I need help creating your TikTok ad. Let me guide you through the steps.",
                    "internal_reasoning": f"LLM returned non-JSON: {response_text[:100]}...",
                    "collected_data": {},
                    "next_step": "continue"
                }
                
        except Exception as e:
            print(f"Error in create_structured_response: {e}")
            return {
                "user_message": "I'm having trouble connecting to the AI service. Let me help you manually.",
                "internal_reasoning": f"NVIDIA API error: {str(e)}",
                "collected_data": {},
                "next_step": "continue"
            }
