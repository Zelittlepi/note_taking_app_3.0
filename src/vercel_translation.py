"""
Vercel-optimized translation handler
"""
import os
import sys
import json
import traceback

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
        
        # Test OpenAI import
        try:
            from openai import OpenAI
            result["debug_info"]["openai_import_success"] = True
        except ImportError as e:
            result["errors"].append(f"OpenAI import failed: {str(e)}")
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
        
        # Create OpenAI client
        try:
            client = OpenAI(
                base_url="https://models.github.ai/inference",
                api_key=github_token,
            )
            result["debug_info"]["openai_client_created"] = True
        except Exception as e:
            result["errors"].append(f"OpenAI client creation failed: {str(e)}")
            return result
        
        # Perform translation
        try:
            translate_title = request_data.get('translate_title', True)
            translate_content = request_data.get('translate_content', True)
            
            translations = {}
            
            if translate_title and note.title:
                response = client.chat.completions.create(
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a professional translator. Translate the given English text to Chinese (Simplified Chinese). Only return the translated text without any additional explanations."
                        },
                        {
                            "role": "user",
                            "content": f"Translate this English text to Chinese: {note.title}"
                        }
                    ],
                    temperature=0.3,
                    top_p=0.9,
                    model="gpt-4o-mini"
                )
                
                translated_title = response.choices[0].message.content.strip()
                translations["title"] = translated_title
                result["debug_info"]["title_translation_success"] = True
            
            if translate_content and note.content:
                response = client.chat.completions.create(
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a professional translator. Translate the given English text to Chinese (Simplified Chinese). Only return the translated text without any additional explanations."
                        },
                        {
                            "role": "user",
                            "content": f"Translate this English text to Chinese: {note.content}"
                        }
                    ],
                    temperature=0.3,
                    top_p=0.9,
                    model="gpt-4o-mini"
                )
                
                translated_content = response.choices[0].message.content.strip()
                translations["content"] = translated_content
                result["debug_info"]["content_translation_success"] = True
            
            # Success
            result["status"] = "success"
            result["translations"] = translations
            result["original_note"] = note.to_dict()
            
            # Backward compatibility
            if "title" in translations:
                result["translated_title"] = translations["title"]
            if "content" in translations:
                result["translated_content"] = translations["content"]
                
        except Exception as e:
            result["errors"].append(f"Translation failed: {str(e)}")
            result["debug_info"]["translation_traceback"] = traceback.format_exc()
            return result
        
    except Exception as e:
        result["errors"].append(f"Unexpected error: {str(e)}")
        result["debug_info"]["main_traceback"] = traceback.format_exc()
    
    return result