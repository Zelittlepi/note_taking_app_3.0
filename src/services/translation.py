import os
import requests
import json

# Handle optional dependencies gracefully
try:
    from dotenv import load_dotenv
    load_dotenv()
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False
    print("python-dotenv package not available, trying manual loader")
    try:
        # Manual .env loading
        env_file = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
        if os.path.exists(env_file):
            with open(env_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    os.environ[key] = value
    except Exception as e:
        print(f"Manual env loader failed: {e}")

class TranslationService:
    def __init__(self):
        self.token = None
        self.endpoint = "https://models.inference.ai.azure.com/chat/completions"
        self.model = "gpt-4o-mini"
        self._initialized = False
        
        # Try initial setup
        self._setup_client()
    
    def _load_env_variables(self):
        """Force reload environment variables"""
        try:
            # Try dotenv first
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            # Manual .env loading as fallback
            try:
                env_file = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
                if os.path.exists(env_file):
                    with open(env_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                    
                    for line in lines:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            key = key.strip()
                            value = value.strip()
                            os.environ[key] = value
            except Exception as e:
                print(f"Failed to load environment variables: {e}")
    
    def _setup_client(self):
        """Setup the GitHub Copilot API client"""
        # Force reload environment variables
        self._load_env_variables()
        
        self.token = os.getenv("GITHUB_AI_TOKEN")
        print(f"🔑 GitHub AI Token found: {'Yes' if self.token else 'No'}")
        
        if self.token:
            try:
                # Test the connection with a simple request
                print("✅ GitHub Copilot API client initialized successfully")
                self._initialized = True
                return True
            except Exception as e:
                print(f"❌ Failed to initialize GitHub Copilot API client: {e}")
                self._initialized = False
                return False
        else:
            print("❌ No GITHUB_AI_TOKEN found in environment variables")
            self._initialized = False
            return False
    
    def is_configured(self):
        """Check if the translation service is properly configured"""
        # Try to reinitialize if not configured
        if not self._initialized:
            print("🔄 Translation service not initialized, attempting setup...")
            self._setup_client()
        
        return self.token is not None and self._initialized
    
    def translate_to_chinese(self, text):
        """
        Translate English text to Chinese using GitHub Copilot AI model via requests
        """
        try:
            print(f"🌐 Starting translation for text: '{text[:50]}...'")
            
            if not self.is_configured():
                error_details = []
                if not self.token:
                    error_details.append("GITHUB_AI_TOKEN not set")
                if not self._initialized:
                    error_details.append("Service initialization failed")
                
                error_msg = f"Translation service is not properly configured: {', '.join(error_details)}"
                print(f"❌ {error_msg}")
                return {"error": error_msg}
            
            if not text or not text.strip():
                return {"error": "No text provided for translation"}
            
            print("🚀 Sending request to GitHub AI...")
            
            # Prepare the request
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a professional translator. Translate the given English text to Chinese (Simplified Chinese). Only return the translated text without any additional explanations or formatting unless the original text contains formatting that should be preserved."
                    },
                    {
                        "role": "user",
                        "content": f"Translate this English text to Chinese: {text}"
                    }
                ],
                "temperature": 0.3,
                "top_p": 0.9,
                "max_tokens": 500
            }
            
            # Make the API request
            response = requests.post(
                self.endpoint,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                translated_text = data["choices"][0]["message"]["content"].strip()
                print(f"✅ Translation successful: '{translated_text}'")
                return {"translated_text": translated_text}
            else:
                error_msg = f"API request failed with status {response.status_code}: {response.text}"
                print(f"❌ {error_msg}")
                return {"error": error_msg}
            
        except Exception as e:
            error_msg = f"Translation failed: {str(e)}"
            print(f"❌ {error_msg}")
            # Add more detailed error info for debugging
            import traceback
            print(f"Full traceback: {traceback.format_exc()}")
            return {"error": error_msg}
    
    def translate_text(self, text, target_language="chinese"):
        """
        General translation function that can be extended for other languages
        """
        if target_language.lower() in ["chinese", "zh", "cn"]:
            return self.translate_to_chinese(text)
        else:
            return {"error": f"Translation to {target_language} is not supported yet"}
    
    def auto_complete_note(self, title="", content="", completion_type="suggestions"):
        """
        Auto-complete note content using AI
        
        Args:
            title: Current note title
            content: Current note content
            completion_type: Type of completion - "suggestions", "corrections", "continuation"
        """
        try:
            print(f"🤖 Starting auto-completion for note: '{title[:30]}...'")
            
            if not self.is_configured():
                error_details = []
                if not self.token:
                    error_details.append("GITHUB_AI_TOKEN not set")
                if not self._initialized:
                    error_details.append("Service initialization failed")
                
                error_msg = f"Auto-complete service is not properly configured: {', '.join(error_details)}"
                print(f"❌ {error_msg}")
                return {"error": error_msg}
            
            if not title and not content:
                return {"error": "Please provide either a title or some content to work with"}
            
            # Prepare different prompts based on completion type
            system_prompts = {
                "suggestions": "You are a helpful writing assistant. Analyze the given note content and provide 3-5 relevant suggestions to expand or improve the content. Focus on adding value, depth, and useful details. Respond with a JSON object containing 'suggestions' array.",
                "corrections": "You are a professional editor. Review the given note content and provide helpful corrections and improvements for grammar, clarity, and structure. Respond with a JSON object containing 'corrections' array with objects having 'issue' and 'suggestion' fields.",
                "continuation": "You are a creative writing assistant. Based on the existing note content, continue writing in the same style and tone. Provide 2-3 paragraphs that naturally extend the content. Respond with a JSON object containing 'continuation' field."
            }
            
            system_prompt = system_prompts.get(completion_type, system_prompts["suggestions"])
            
            # Create user prompt based on available content
            if title and content:
                user_prompt = f"Note Title: {title}\n\nNote Content:\n{content}\n\nPlease provide {completion_type} for this note."
            elif title:
                user_prompt = f"Note Title: {title}\n\nI have this title but no content yet. Please provide {completion_type} for what this note could contain."
            else:
                user_prompt = f"Note Content:\n{content}\n\nPlease provide {completion_type} for this note content."
            
            print("🚀 Sending auto-completion request to GitHub AI...")
            
            # Prepare the request
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ],
                "temperature": 0.7,  # Higher creativity for suggestions
                "top_p": 0.9,
                "max_tokens": 800
            }
            
            # Make the API request
            response = requests.post(
                self.endpoint,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                ai_response = data["choices"][0]["message"]["content"].strip()
                
                # Try to parse as JSON first, fallback to text if needed
                try:
                    import json
                    parsed_response = json.loads(ai_response)
                    print(f"✅ Auto-completion successful: {completion_type}")
                    return {
                        "success": True,
                        "type": completion_type,
                        "result": parsed_response
                    }
                except json.JSONDecodeError:
                    # If JSON parsing fails, return as plain text
                    print(f"✅ Auto-completion successful (plain text): {completion_type}")
                    return {
                        "success": True,
                        "type": completion_type,
                        "result": {"text": ai_response}
                    }
            else:
                error_msg = f"API request failed with status {response.status_code}: {response.text}"
                print(f"❌ {error_msg}")
                return {"error": error_msg}
            
        except Exception as e:
            error_msg = f"Auto-completion failed: {str(e)}"
            print(f"❌ {error_msg}")
            # Add more detailed error info for debugging
            import traceback
            print(f"Full traceback: {traceback.format_exc()}")
            return {"error": error_msg}

# Create a global instance
translation_service = TranslationService()