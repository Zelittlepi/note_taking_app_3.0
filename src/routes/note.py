from flask import Blueprint, jsonify, request
import os
import traceback
from src.models.note import Note, db

# Import translation service with error handling
try:
    from src.services.translation import translation_service
    TRANSLATION_AVAILABLE = True
except Exception as e:
    print(f"Translation service not available: {e}")
    TRANSLATION_AVAILABLE = False
    translation_service = None

note_bp = Blueprint('note', __name__)

@note_bp.route('/notes', methods=['GET'])
def get_notes():
    """Get all notes, ordered by most recently updated"""
    notes = Note.query.order_by(Note.updated_at.desc()).all()
    return jsonify([note.to_dict() for note in notes])

@note_bp.route('/notes', methods=['POST'])
def create_note():
    """Create a new note"""
    try:
        data = request.json
        if not data or 'title' not in data or 'content' not in data:
            return jsonify({'error': 'Title and content are required'}), 400
        
        note = Note(title=data['title'], content=data['content'])
        db.session.add(note)
        db.session.commit()
        return jsonify(note.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@note_bp.route('/notes/<int:note_id>', methods=['GET'])
def get_note(note_id):
    """Get a specific note by ID"""
    note = Note.query.get_or_404(note_id)
    return jsonify(note.to_dict())

@note_bp.route('/notes/<int:note_id>', methods=['PUT'])
def update_note(note_id):
    """Update a specific note"""
    try:
        note = Note.query.get_or_404(note_id)
        data = request.json
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        note.title = data.get('title', note.title)
        note.content = data.get('content', note.content)
        db.session.commit()
        return jsonify(note.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@note_bp.route('/notes/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    """Delete a specific note"""
    try:
        note = Note.query.get_or_404(note_id)
        db.session.delete(note)
        db.session.commit()
        return '', 204
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@note_bp.route('/notes/search', methods=['GET'])
def search_notes():
    """Search notes by title or content"""
    query = request.args.get('q', '')
    if not query:
        return jsonify([])
    
    notes = Note.query.filter(
        (Note.title.contains(query)) | (Note.content.contains(query))
    ).order_by(Note.updated_at.desc()).all()
    
    return jsonify([note.to_dict() for note in notes])

@note_bp.route('/notes/<int:note_id>/translate', methods=['POST'])
def translate_note(note_id):
    """Translate a note's content from English to Chinese"""
    try:
        # Check if we're in a serverless environment (Vercel)
        is_vercel = os.getenv('VERCEL') == '1' or 'vercel' in os.getenv('DEPLOYMENT_URL', '').lower()
        
        if is_vercel:
            # Use Vercel-optimized handler
            try:
                from src.vercel_translation import handle_translation_request
                request_data = request.json or {}
                result = handle_translation_request(note_id, request_data)
                
                if result["status"] == "success":
                    return jsonify(result), 200
                else:
                    return jsonify({
                        "error": "Translation failed",
                        "details": result["errors"],
                        "debug_info": result["debug_info"]
                    }), 500
            except Exception as e:
                return jsonify({
                    "error": "Vercel translation handler failed",
                    "details": str(e),
                    "traceback": traceback.format_exc()
                }), 500
        
        # Original handler for local development
        if not TRANSLATION_AVAILABLE or not translation_service:
            return jsonify({
                'error': 'Translation service is not available',
                'details': 'Translation service failed to initialize'
            }), 503
        
        # Get the note
        try:
            note = Note.query.get_or_404(note_id)
        except Exception as e:
            return jsonify({
                'error': 'Note not found',
                'details': str(e)
            }), 404
        
        # Parse request data
        data = request.json or {}
        
        # Determine what to translate
        translate_title = data.get('translate_title', True)
        translate_content = data.get('translate_content', True)
        
        result = {
            'original_note': note.to_dict(),
            'translations': {}
        }
        
        # Translate title if requested
        if translate_title and note.title:
            try:
                title_result = translation_service.translate_to_chinese(note.title)
                if 'error' in title_result:
                    return jsonify({
                        'error': 'Title translation failed',
                        'details': title_result['error']
                    }), 500
                result['translations']['title'] = title_result['translated_text']
                result['translated_title'] = title_result['translated_text']  # Backward compatibility
            except Exception as e:
                return jsonify({
                    'error': 'Title translation failed',
                    'details': str(e)
                }), 500
        
        # Translate content if requested
        if translate_content and note.content:
            try:
                content_result = translation_service.translate_to_chinese(note.content)
                if 'error' in content_result:
                    return jsonify({
                        'error': 'Content translation failed',
                        'details': content_result['error']
                    }), 500
                result['translations']['content'] = content_result['translated_text']
                result['translated_content'] = content_result['translated_text']  # Backward compatibility
            except Exception as e:
                return jsonify({
                    'error': 'Content translation failed',
                    'details': str(e)
                }), 500
        
        return jsonify(result)
        
    except Exception as e:
        import traceback
        return jsonify({
            'error': 'Translation request failed',
            'details': str(e),
            'traceback': traceback.format_exc() if os.getenv('FLASK_ENV') == 'development' else None
        }), 500

@note_bp.route('/translate', methods=['POST'])
def translate_text():
    """Translate arbitrary text from English to Chinese"""
    try:
        if not TRANSLATION_AVAILABLE or not translation_service:
            return jsonify({'error': 'Translation service is not available'}), 503
            
        data = request.json
        if not data or 'text' not in data:
            return jsonify({'error': 'Text is required for translation'}), 400
        
        text = data['text']
        target_language = data.get('target_language', 'chinese')
        
        result = translation_service.translate_text(text, target_language)
        
        if 'error' in result:
            return jsonify(result), 500
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@note_bp.route('/debug/translation-status', methods=['GET'])
def debug_translation_status():
    """Debug endpoint to check translation service status"""
    debug_info = {
        "translation_service_imported": TRANSLATION_AVAILABLE,
        "translation_service_exists": translation_service is not None,
        "environment_variables": {
            "GITHUB_AI_TOKEN": bool(os.getenv('GITHUB_AI_TOKEN')),
            "FLASK_ENV": os.getenv('FLASK_ENV', 'not_set')
        },
        "requests_available": False,
        "service_configured": False
    }
    
    # Test requests import
    try:
        import requests
        debug_info["requests_available"] = True
        debug_info["requests_version"] = requests.__version__
    except ImportError as e:
        debug_info["requests_import_error"] = str(e)
    
    # Test translation service
    if TRANSLATION_AVAILABLE and translation_service:
        try:
            debug_info["service_configured"] = translation_service.is_configured()
            debug_info["service_token_exists"] = translation_service.token is not None
        except Exception as e:
            debug_info["service_check_error"] = str(e)
    
    return jsonify(debug_info)

@note_bp.route('/auto-complete', methods=['POST'])
def auto_complete_note():
    """Auto-complete note content using AI"""
    try:
        data = request.json or {}
        title = data.get('title', '').strip()
        content = data.get('content', '').strip()
        completion_type = data.get('type', 'suggestions')  # suggestions, corrections, continuation
        
        # Validate completion type
        valid_types = ['suggestions', 'corrections', 'continuation']
        if completion_type not in valid_types:
            return jsonify({
                'error': f'Invalid completion type. Must be one of: {", ".join(valid_types)}'
            }), 400
        
        if not title and not content:
            return jsonify({
                'error': 'Please provide either a title or content to work with'
            }), 400
        
        # Check if translation service is available
        if not TRANSLATION_AVAILABLE:
            return jsonify({
                'error': 'Auto-completion service is not available'
            }), 503
        
        print(f"🤖 Auto-completion request: type={completion_type}, title='{title[:30]}...', content_len={len(content)}")
        
        # Use translation service for auto-completion
        result = translation_service.auto_complete_note(
            title=title,
            content=content,
            completion_type=completion_type
        )
        
        if 'error' in result:
            return jsonify({
                'error': 'Auto-completion failed',
                'details': result['error']
            }), 500
        
        return jsonify(result)
        
    except Exception as e:
        import traceback
        print(f"❌ Auto-completion endpoint error: {e}")
        return jsonify({
            'error': 'Auto-completion request failed',
            'details': str(e),
            'traceback': traceback.format_exc() if os.getenv('FLASK_ENV') == 'development' else None
        }), 500

@note_bp.route('/notes/<int:note_id>/auto-complete', methods=['POST'])
def auto_complete_existing_note(note_id):
    """Auto-complete content for an existing note"""
    try:
        # Get the note from database
        note = Note.query.get_or_404(note_id)
        
        data = request.json or {}
        completion_type = data.get('type', 'suggestions')
        
        # Validate completion type
        valid_types = ['suggestions', 'corrections', 'continuation']
        if completion_type not in valid_types:
            return jsonify({
                'error': f'Invalid completion type. Must be one of: {", ".join(valid_types)}'
            }), 400
        
        # Check if translation service is available
        if not TRANSLATION_AVAILABLE:
            return jsonify({
                'error': 'Auto-completion service is not available'
            }), 503
        
        print(f"🤖 Auto-completion for note {note_id}: type={completion_type}")
        
        # Use translation service for auto-completion
        result = translation_service.auto_complete_note(
            title=note.title or '',
            content=note.content or '',
            completion_type=completion_type
        )
        
        if 'error' in result:
            return jsonify({
                'error': 'Auto-completion failed',
                'details': result['error']
            }), 500
        
        # Add note information to response
        result['note'] = note.to_dict()
        
        return jsonify(result)
        
    except Exception as e:
        import traceback
        print(f"❌ Auto-completion endpoint error: {e}")
        return jsonify({
            'error': 'Auto-completion request failed',
            'details': str(e),
            'traceback': traceback.format_exc() if os.getenv('FLASK_ENV') == 'development' else None
        }), 500

@note_bp.route('/test/vercel-translation/<int:note_id>', methods=['POST'])
def test_vercel_translation(note_id):
    """Test endpoint specifically for debugging Vercel translation issues"""
    try:
        from src.vercel_translation import handle_translation_request
        request_data = request.json or {}
        result = handle_translation_request(note_id, request_data)
        return jsonify(result), 200 if result["status"] == "success" else 500
    except Exception as e:
        return jsonify({
            "error": "Test endpoint failed",
            "details": str(e),
            "traceback": traceback.format_exc()
        }), 500

