import requests
import json
from typing import List, Dict, Any, Optional

class DeepSeekClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.deepseek.com/v1"
        self.model = "deepseek-chat"
        
    def generate_response(self, system_prompt: str, chat_history: List[Dict[str, Any]], 
                         user_message: str, reply_context: Optional[str] = None,
                         max_tokens: int = 500) -> Optional[str]:
        """Generate a response using DeepSeek API with configurable max_tokens."""
        
        # Format chat history for context
        context_messages = []
        
        # Add system prompt
        context_messages.append({
            "role": "system",
            "content": system_prompt
        })
        
        # Add chat history as context
        if chat_history:
            # Enhanced history with reply tracking
            enhanced_history = []
            for msg in chat_history:
                enhanced_msg = msg.copy()
                if msg.get('reply_to_message_id'):
                    enhanced_msg['reply_info'] = f"(replying to message {msg['reply_to_message_id']})"
                enhanced_history.append(enhanced_msg)
            
            history_text = "RECENT CHAT HISTORY:\n"
            history_text += json.dumps(enhanced_history, ensure_ascii=False, indent=2)
            history_text += "\n\nBased on this chat history, respond to the latest message."
            
            context_messages.append({
                "role": "system",
                "content": history_text
            })
        
        # Add reply context if available
        if reply_context:
            context_messages.append({
                "role": "system",
                "content": reply_context
            })
        
        # Add the current message
        context_messages.append({
            "role": "user",
            "content": user_message
        })
        
        # Prepare the API request
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Adjust parameters based on max_tokens (assistant mode gets different settings)
        if max_tokens > 1000:  # Assistant mode
            temperature = 0.7
            top_p = 0.9
            frequency_penalty = 0.1
            presence_penalty = 0.1
        else:  # Chat mode
            temperature = 1.3
            top_p = 0.95
            frequency_penalty = 0.3
            presence_penalty = 0.3
        
        payload = {
            "model": self.model,
            "messages": context_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p,
            "frequency_penalty": frequency_penalty,
            "presence_penalty": presence_penalty
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return data['choices'][0]['message']['content'].strip()
            else:
                print(f"DeepSeek API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error calling DeepSeek API: {e}")
            return None
    
    def test_connection(self) -> bool:
        """Test the connection to DeepSeek API."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        test_payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": "Test"}],
            "max_tokens": 10
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=test_payload,
                timeout=10
            )
            return response.status_code == 200
        except Exception:
            return False