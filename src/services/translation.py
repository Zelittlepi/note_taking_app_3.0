import os

# Handle optional dependencies gracefully
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("OpenAI package not available")

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
        self.client = None
        self.token = None
        self.endpoint = "https://models.github.ai/inference"
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
        """Setup the OpenAI client"""
        if not OPENAI_AVAILABLE:
            print("❌ OpenAI package not available")
            return False
        
        # Force reload environment variables
        self._load_env_variables()
        
        self.token = os.getenv("GITHUB_AI_TOKEN")
        print(f"🔑 GitHub AI Token found: {'Yes' if self.token else 'No'}")
        
        if self.token:
            try:
                self.client = OpenAI(
                    base_url=self.endpoint,
                    api_key=self.token,
                )
                # Test the client with a simple call
                print("🔄 Testing OpenAI client connection...")
                # Don't actually make a call during init, just create the client
                print("✅ OpenAI client initialized successfully")
                self._initialized = True
                return True
            except Exception as e:
                print(f"❌ Failed to initialize OpenAI client: {e}")
                self.client = None
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
        
        return OPENAI_AVAILABLE and self.client is not None and self.token is not None and self._initialized
    
    def translate_to_chinese(self, text):
        """
        Translate English text to Chinese using GitHub Copilot AI model
        """
        try:
            print(f"🌐 Starting translation for text: '{text[:50]}...'")
            
            if not OPENAI_AVAILABLE:
                return {"error": "Translation service is not available - OpenAI package not installed"}
            
            if not self.is_configured():
                error_details = []
                if not OPENAI_AVAILABLE:
                    error_details.append("OpenAI package not available")
                if not self.token:
                    error_details.append("GITHUB_AI_TOKEN not set")
                if not self.client:
                    error_details.append("OpenAI client not initialized")
                if not self._initialized:
                    error_details.append("Service initialization failed")
                
                error_msg = f"Translation service is not properly configured: {', '.join(error_details)}"
                print(f"❌ {error_msg}")
                return {"error": error_msg}
            
            if not text or not text.strip():
                return {"error": "No text provided for translation"}
            
            print("🚀 Sending request to GitHub AI...")
            
            response = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional translator. Translate the given English text to Chinese (Simplified Chinese). Only return the translated text without any additional explanations or formatting unless the original text contains formatting that should be preserved."
                    },
                    {
                        "role": "user",
                        "content": f"Translate this English text to Chinese: {text}"
                    }
                ],
                temperature=0.3,  # Lower temperature for more consistent translations
                top_p=0.9,
                model=self.model
            )
            
            translated_text = response.choices[0].message.content.strip()
            print(f"✅ Translation successful: '{translated_text}'")
            return {"translated_text": translated_text}
            
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

# Create a global instance
translation_service = TranslationService()