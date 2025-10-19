"""
Minimal Flask app for Vercel deployment
This version handles missing dependencies gracefully
"""
import os
import sys

# Add project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS

# Create Flask app
app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), '..', 'src', 'static'))
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default-secret-key')

# Enable CORS
CORS(app)

# Try to import and initialize database components
db = None
Note = None
User = None

try:
    from flask_sqlalchemy import SQLAlchemy
    db = SQLAlchemy()
    
    # Configure database
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    
    # Import models
    from src.models.note import Note
    from src.models.user import User
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    DATABASE_AVAILABLE = True
    
except Exception as e:
    print(f"Database initialization failed: {e}")
    DATABASE_AVAILABLE = False

# Try to import translation service
TRANSLATION_AVAILABLE = False
translation_service = None

try:
    from src.services.translation import translation_service
    TRANSLATION_AVAILABLE = True
except Exception as e:
    print(f"Translation service not available: {e}")

# Health check endpoint
@app.route('/api/health')
def health_check():
    return jsonify({
        "status": "ok",
        "message": "NoteTaker API is running",
        "database_available": DATABASE_AVAILABLE,
        "translation_available": TRANSLATION_AVAILABLE
    })

# Notes endpoints (only if database is available)
if DATABASE_AVAILABLE and Note:
    
    @app.route('/api/notes', methods=['GET'])
    def get_notes():
        try:
            notes = Note.query.order_by(Note.updated_at.desc()).all()
            return jsonify([note.to_dict() for note in notes])
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/notes', methods=['POST'])
    def create_note():
        try:
            data = request.json
            if not data or 'title' not in data or 'content' not in data:
                return jsonify({'error': 'Title and content are required'}), 400
            
            note = Note(title=data['title'], content=data['content'])
            db.session.add(note)
            db.session.commit()
            return jsonify(note.to_dict()), 201
        except Exception as e:
            if db:
                db.session.rollback()
            return jsonify({'error': str(e)}), 500

    @app.route('/api/notes/<int:note_id>', methods=['GET'])
    def get_note(note_id):
        try:
            note = Note.query.get_or_404(note_id)
            return jsonify(note.to_dict())
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/notes/<int:note_id>', methods=['PUT'])
    def update_note(note_id):
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
            if db:
                db.session.rollback()
            return jsonify({'error': str(e)}), 500

    @app.route('/api/notes/<int:note_id>', methods=['DELETE'])
    def delete_note(note_id):
        try:
            note = Note.query.get_or_404(note_id)
            db.session.delete(note)
            db.session.commit()
            return '', 204
        except Exception as e:
            if db:
                db.session.rollback()
            return jsonify({'error': str(e)}), 500

    @app.route('/api/notes/search', methods=['GET'])
    def search_notes():
        try:
            query = request.args.get('q', '')
            if not query:
                return jsonify([])
            
            notes = Note.query.filter(
                (Note.title.contains(query)) | (Note.content.contains(query))
            ).order_by(Note.updated_at.desc()).all()
            
            return jsonify([note.to_dict() for note in notes])
        except Exception as e:
            return jsonify({'error': str(e)}), 500

# Translation endpoints (only if translation service is available)
if TRANSLATION_AVAILABLE and translation_service:
    
    @app.route('/api/notes/<int:note_id>/translate', methods=['POST'])
    def translate_note(note_id):
        try:
            if not DATABASE_AVAILABLE or not Note:
                return jsonify({'error': 'Database not available'}), 503
                
            note = Note.query.get_or_404(note_id)
            data = request.json or {}
            
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
            
            result['original_note'] = note.to_dict()
            return jsonify(result)
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/translate', methods=['POST'])
    def translate_text():
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

else:
    # Fallback translation endpoints
    @app.route('/api/notes/<int:note_id>/translate', methods=['POST'])
    def translate_note_fallback(note_id):
        return jsonify({'error': 'Translation service is not available'}), 503

    @app.route('/api/translate', methods=['POST'])
    def translate_text_fallback():
        return jsonify({'error': 'Translation service is not available'}), 503

# Static file serving
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404

if __name__ == '__main__':
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5001))
    debug = os.getenv('FLASK_ENV') == 'development'
    app.run(host=host, port=port, debug=debug)