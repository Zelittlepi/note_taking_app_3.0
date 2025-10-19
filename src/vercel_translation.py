"""
Vercel-optimized translation handler using requests library
"""
import os
import sys
import json
import traceback
import requests

def handle_translation_request(note_id, request_data):
    """
    Handle translation request with comprehensive error handling for Vercel
    """
    result = {
        "status": "error",
        "note_id": note_id,
        "request_data": request_data,
        "debug_info": {},
        "errors": []
    }
    
    try:
        # Check environment
        github_token = os.getenv('GITHUB_AI_TOKEN')
        result["debug_info"]["github_token_available"] = bool(github_token)
        
        if not github_token:
            result["errors"].append("GITHUB_AI_TOKEN environment variable not set")
            return result
        
        # Test requests import
        try:
            result["debug_info"]["requests_available"] = True
            result["debug_info"]["requests_version"] = requests.__version__
        except ImportError as e:
            result["errors"].append(f"Requests import failed: {str(e)}")
            return result
        
        # Test database connection
        try:
            from src.models.note import Note
            note = Note.query.get(note_id)
            if not note:
                result["errors"].append(f"Note with ID {note_id} not found")
                return result
            result["debug_info"]["note_found"] = True
            result["debug_info"]["note_title"] = note.title
            result["debug_info"]["note_content_length"] = len(note.content) if note.content else 0
        except Exception as e:
            result["errors"].append(f"Database query failed: {str(e)}")
            return result
        
        # Setup API endpoint and headers
        endpoint = "https://models.inference.ai.azure.com/chat/completions"
        headers = {
            "Authorization": f"Bearer {github_token}",
            "Content-Type": "application/json"
        }
        result["debug_info"]["api_endpoint"] = endpoint
        
        # Perform translation
        try:
            translate_title = request_data.get('translate_title', True)
            translate_content = request_data.get('translate_content', True)
            
            translations = {}
            
            if translate_title and note.title:
                payload = {
                    "model": "gpt-4o-mini",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a professional translator. Translate the given English text to Chinese (Simplified Chinese). Only return the translated text without any additional explanations."
                        },
                        {
                            "role": "user",
                            "content": f"Translate this English text to Chinese: {note.title}"
                        }
                    ],
                    "temperature": 0.3,
                    "top_p": 0.9,
                    "max_tokens": 500
                }
                
                response = requests.post(endpoint, headers=headers, json=payload, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    translated_title = data["choices"][0]["message"]["content"].strip()
                    translations["title"] = translated_title
                    result["debug_info"]["title_translation_success"] = True
                else:
                    result["errors"].append(f"Title translation API failed: {response.status_code} - {response.text}")
            
            if translate_content and note.content:
                payload = {
                    "model": "gpt-4o-mini",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a professional translator. Translate the given English text to Chinese (Simplified Chinese). Only return the translated text without any additional explanations."
                        },
                        {
                            "role": "user",
                            "content": f"Translate this English text to Chinese: {note.content}"
                        }
                    ],
                    "temperature": 0.3,
                    "top_p": 0.9,
                    "max_tokens": 1000
                }
                
                response = requests.post(endpoint, headers=headers, json=payload, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    translated_content = data["choices"][0]["message"]["content"].strip()
                    translations["content"] = translated_content
                    result["debug_info"]["content_translation_success"] = True
                else:
                    result["errors"].append(f"Content translation API failed: {response.status_code} - {response.text}")
            
            # Success if we have any translations
            if translations:
                result["status"] = "success"
                result["translations"] = translations
                result["original_note"] = note.to_dict()
                
                # Backward compatibility
                if "title" in translations:
                    result["translated_title"] = translations["title"]
                if "content" in translations:
                    result["translated_content"] = translations["content"]
            else:
                result["errors"].append("No translations were performed")
                
        except Exception as e:
            result["errors"].append(f"Translation failed: {str(e)}")
            result["debug_info"]["translation_traceback"] = traceback.format_exc()
            return result
        
    except Exception as e:
        result["errors"].append(f"Unexpected error: {str(e)}")
        result["debug_info"]["main_traceback"] = traceback.format_exc()
    
    return result