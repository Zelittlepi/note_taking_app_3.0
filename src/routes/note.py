from flask import Blueprint, jsonify, request
from src.models.note import Note, db
from src.services.translation import translation_service

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
        note = Note.query.get_or_404(note_id)
        data = request.json
        
        # Determine what to translate
        translate_title = data.get('translate_title', True)
        translate_content = data.get('translate_content', True)
        
        result = {}
        
        if translate_title and note.title:
            title_result = translation_service.translate_to_chinese(note.title)
            if 'error' in title_result:
                return jsonify({'error': f'Title translation failed: {title_result["error"]}'}), 500
            result['translated_title'] = title_result['translated_text']
        
        if translate_content and note.content:
            content_result = translation_service.translate_to_chinese(note.content)
            if 'error' in content_result:
                return jsonify({'error': f'Content translation failed: {content_result["error"]}'}), 500
            result['translated_content'] = content_result['translated_text']
        
        # Include original note data
        result['original_note'] = note.to_dict()
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@note_bp.route('/translate', methods=['POST'])
def translate_text():
    """Translate arbitrary text from English to Chinese"""
    try:
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

