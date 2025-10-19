"""
Debug version of translation service to identify the exact issue
"""
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

def debug_translation_service():
    print("🔍 Debugging Translation Service")
    print("=" * 50)
    
    # Load environment manually
    env_file = '.env'
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            lines = f.readlines()
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()
        print("✅ Environment variables loaded")
    else:
        print("❌ .env file not found")
    
    # Check token
    token = os.getenv("GITHUB_AI_TOKEN")
    print(f"🔑 Token available: {'Yes' if token else 'No'}")
    
    # Check OpenAI availability
    try:
        from openai import OpenAI
        print("✅ OpenAI package is available")
        openai_available = True
    except ImportError as e:
        print(f"❌ OpenAI package not available: {e}")
        openai_available = False
    
    if openai_available and token:
        try:
            # Try to create client
            client = OpenAI(
                base_url="https://models.github.ai/inference",
                api_key=token,
            )
            print("✅ OpenAI client created successfully")
            
            # Test import of translation service
            try:
                from src.services.translation import translation_service
                print("✅ Translation service imported")
                
                print(f"Service configured: {translation_service.is_configured()}")
                print(f"Service client: {'Yes' if translation_service.client else 'No'}")
                print(f"Service token: {'Yes' if translation_service.token else 'No'}")
                
                if translation_service.is_configured():
                    result = translation_service.translate_to_chinese("Hello")
                    if 'error' in result:
                        print(f"❌ Translation test failed: {result['error']}")
                    else:
                        print(f"✅ Translation test successful: {result['translated_text']}")
                else:
                    print("❌ Translation service not properly configured")
                
            except Exception as e:
                print(f"❌ Translation service import/test failed: {e}")
                import traceback
                traceback.print_exc()
                
        except Exception as e:
            print(f"❌ OpenAI client creation failed: {e}")
    else:
        if not openai_available:
            print("❌ Cannot test - OpenAI package not available")
        if not token:
            print("❌ Cannot test - no token available")

if __name__ == "__main__":
    debug_translation_service()