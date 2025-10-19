import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class TranslationService:
    def __init__(self):
        self.token = os.getenv("GITHUB_AI_TOKEN")
        self.endpoint = "https://models.github.ai/inference"
        self.model = "openai/gpt-4o-mini"
        
        self.client = OpenAI(
            base_url=self.endpoint,
            api_key=self.token,
        )
    
    def translate_to_chinese(self, text):
        """
        Translate English text to Chinese using GitHub Copilot AI model
        """
        try:
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