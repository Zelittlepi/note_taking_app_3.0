"""
Direct translation test using the actual OpenAI client
"""
import os

# Manually load environment variables
env_file = '.env'
if os.path.exists(env_file):
    with open(env_file, 'r') as f:
        lines = f.readlines()
    
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            key, value = line.split('=', 1)
            os.environ[key.strip()] = value.strip()

# Now test the translation
token = os.getenv("GITHUB_AI_TOKEN")
print(f"Token available: {'Yes' if token else 'No'}")

if token:
    try:
        # Import openai after setting environment
        from openai import OpenAI
        
        client = OpenAI(
            base_url="https://models.github.ai/inference",
            api_key=token,
        )
        
        print("Testing translation...")
        
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional translator. Translate the given English text to Chinese (Simplified Chinese). Only return the translated text without any additional explanations."
                },
                {
                    "role": "user",
                    "content": "Translate this English text to Chinese: Hello, how are you?"
                }
            ],
            temperature=0.3,
            top_p=0.9,
            model="gpt-4o-mini"
        )
        
        translated_text = response.choices[0].message.content.strip()
        print(f"✅ Translation successful: {translated_text}")
        
    except Exception as e:
        print(f"❌ Translation failed: {e}")
else:
    print("❌ No GitHub AI token found")