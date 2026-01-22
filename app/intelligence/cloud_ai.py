import httpx
import json

class CloudAIEngine:
    """OpenRouter-based cloud AI engine."""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        
    def generate(self, prompt: str, context: str = "") -> str:
        """Generate AI response using OpenRouter."""
        if not self.api_key:
            return "⚠️ Cloud AI: No API key configured. Please add your OpenRouter API key in Settings."
        
        try:
            full_prompt = f"{context}\n\nUser: {prompt}" if context else prompt
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            
            payload = {
                "model": "mistralai/mistral-7b-instruct",  # Free tier model
                "messages": [
                    {
                        "role": "system",
                        "content": "You are SysSentinel AI, a helpful system monitoring assistant. Provide concise, technical answers about system performance and diagnostics."
                    },
                    {
                        "role": "user",
                        "content": full_prompt
                    }
                ],
                "max_tokens": 500,
            }
            
            with httpx.Client(timeout=30.0) as client:
                response = client.post(
                    self.base_url,
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data["choices"][0]["message"]["content"]
                elif response.status_code == 401:
                    return "⚠️ Cloud AI: Invalid API key. Please check your OpenRouter API key in Settings."
                else:
                    return f"⚠️ Cloud AI Error: {response.status_code} - {response.text[:100]}"
                    
        except httpx.TimeoutException:
            return "⚠️ Cloud AI: Request timed out. Please try again."
        except Exception as e:
            return f"⚠️ Cloud AI Error: {str(e)}"
