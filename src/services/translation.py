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
        
        if not OPENAI_AVAILABLE:
            print("OpenAI package not available")
            return
            
        self.token = os.getenv("GITHUB_AI_TOKEN")
        print(f"GitHub AI Token found: {'Yes' if self.token else 'No'}")
        
        if self.token:
            try:
                self.client = OpenAI(
                    base_url=self.endpoint,
                    api_key=self.token,
                )
                print("OpenAI client initialized successfully")
            except Exception as e:
                print(f"Failed to initialize OpenAI client: {e}")
                self.client = None
        else:
            print("No GITHUB_AI_TOKEN found in environment variables")
    
    def is_configured(self):
        """Check if the translation service is properly configured"""
        return OPENAI_AVAILABLE and self.client is not None and self.token is not None
    
    def translate_to_chinese(self, text):
        """
        Translate English text to Chinese using GitHub Copilot AI model
        """
        try:
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
                return {"error": f"Translation service is not properly configured: {', '.join(error_details)}"}
            
            if not text or not text.strip():
                return {"error": "No text provided for translation"}
            
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
            return {"translated_text": translated_text}
            
        except Exception as e:
            return {"error": f"Translation failed: {str(e)}"}
    
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