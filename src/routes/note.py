from flask import Blueprint, jsonify, request
import os
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
        # Check if translation service is available
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
        "openai_available": False,
        "service_configured": False
    }
    
    # Test OpenAI import
    try:
        import openai
        debug_info["openai_available"] = True
        debug_info["openai_version"] = openai.__version__
    except ImportError as e:
        debug_info["openai_import_error"] = str(e)
    
    # Test translation service
    if TRANSLATION_AVAILABLE and translation_service:
        try:
            debug_info["service_configured"] = translation_service.is_configured()
            debug_info["service_client_exists"] = translation_service.client is not None
            debug_info["service_token_exists"] = translation_service.token is not None
        except Exception as e:
            debug_info["service_check_error"] = str(e)
    
    return jsonify(debug_info)

