from flask import Blueprint, jsonify, request, make_response
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

@note_bp.route('/notes/<int:note_id>/export', methods=['GET'])
def export_note(note_id):
    """Export a single note as Markdown file"""
    try:
        note = Note.query.get_or_404(note_id)
        
        # Generate Markdown content
        markdown_content = generate_note_markdown(note)
        
        # Create safe filename
        safe_title = "".join(c for c in (note.title or "untitled") if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_title = safe_title.replace(' ', '_')[:50]  # Limit length
        filename = f"{safe_title}.md"
        
        # Return file as download
        response = make_response(markdown_content)
        response.headers['Content-Type'] = 'text/markdown; charset=utf-8'
        response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
        
    except Exception as e:
        return jsonify({
            'error': 'Export failed',
            'details': str(e)
        }), 500

@note_bp.route('/notes/export-all', methods=['GET'])
def export_all_notes():
    """Export all notes as a single Markdown file or ZIP archive"""
    try:
        notes = Note.query.order_by(Note.created_at.desc()).all()
        
        if not notes:
            return jsonify({'error': 'No notes to export'}), 404
        
        # Generate combined Markdown content
        markdown_content = generate_all_notes_markdown(notes)
        
        # Create filename with timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"all_notes_{timestamp}.md"
        
        # Return file as download
        response = make_response(markdown_content)
        response.headers['Content-Type'] = 'text/markdown; charset=utf-8'
        response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
        
    except Exception as e:
        return jsonify({
            'error': 'Bulk export failed',
            'details': str(e)
        }), 500

def generate_note_markdown(note):
    """Convert a note to Markdown format"""
    from datetime import datetime
    
    # Start with frontmatter (YAML metadata)
    markdown = "---\n"
    markdown += f"title: \"{note.title or 'Untitled'}\"\n"
    markdown += f"id: {note.id}\n"
    
    if note.created_at:
        markdown += f"created: {note.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
    if note.updated_at:
        markdown += f"updated: {note.updated_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
    
    markdown += "---\n\n"
    
    # Add title as main heading
    markdown += f"# {note.title or 'Untitled'}\n\n"
    
    # Add content
    if note.content:
        # Clean up content and ensure proper Markdown formatting
        content = note.content.strip()
        
        # If content doesn't start with Markdown headers, treat as paragraphs
        if not content.startswith('#'):
            # Split into paragraphs and ensure proper spacing
            paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
            content = '\n\n'.join(paragraphs)
        
        markdown += content + "\n\n"
    else:
        markdown += "*No content*\n\n"
    
    # Add metadata footer
    markdown += "---\n"
    markdown += f"*Exported from NoteTaker on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"
    
    return markdown

def generate_all_notes_markdown(notes):
    """Convert all notes to a combined Markdown format"""
    from datetime import datetime
    
    # Start with document header
    markdown = f"# All Notes Export\n\n"
    markdown += f"*Exported from NoteTaker on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
    markdown += f"**Total Notes:** {len(notes)}\n\n"
    markdown += "---\n\n"
    
    # Add table of contents
    markdown += "## Table of Contents\n\n"
    for i, note in enumerate(notes, 1):
        title = note.title or 'Untitled'
        # Create anchor link (lowercase, spaces to hyphens, remove special chars)
        anchor = title.lower().replace(' ', '-')
        anchor = ''.join(c for c in anchor if c.isalnum() or c == '-')
        markdown += f"{i}. [{title}](#{anchor})\n"
    markdown += "\n---\n\n"
    
    # Add each note
    for i, note in enumerate(notes, 1):
        # Note header
        markdown += f"## {i}. {note.title or 'Untitled'}\n\n"
        
        # Note metadata
        markdown += f"**ID:** {note.id}  \n"
        if note.created_at:
            markdown += f"**Created:** {note.created_at.strftime('%Y-%m-%d %H:%M:%S')}  \n"
        if note.updated_at:
            markdown += f"**Updated:** {note.updated_at.strftime('%Y-%m-%d %H:%M:%S')}  \n"
        markdown += "\n"
        
        # Note content
        if note.content:
            content = note.content.strip()
            markdown += content + "\n\n"
        else:
            markdown += "*No content*\n\n"
        
        # Separator between notes
        if i < len(notes):
            markdown += "---\n\n"
    
    return markdown

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

