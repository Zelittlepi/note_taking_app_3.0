import sys
import os
import traceback

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def create_fallback_app():
    """Create a minimal Flask app with error reporting"""
    from flask import Flask, jsonify, request
    from flask_cors import CORS
    
    app = Flask(__name__)
    CORS(app)
    
    @app.route('/api/health')
    def health():
        return jsonify({
            "status": "fallback", 
            "message": "Running in fallback mode - main app import failed"
        })
    
    @app.route('/api/notes/<int:note_id>/translate', methods=['POST'])
    def translate_note_fallback(note_id):
        return jsonify({
            "error": "Translation service is not available - app running in fallback mode"
        }), 503
    
    @app.route('/')
    def index():
        return jsonify({
            "message": "NoteTaker API - Fallback Mode",
            "status": "limited_functionality"
        })
    
    return app

# Try to import the main app, fallback to minimal version
app = None
import_error = None

try:
    from src.main import app
    print("✅ Successfully imported main app")
except Exception as e:
    import_error = str(e)
    print(f"❌ Error importing main app: {e}")
    print(f"Traceback: {traceback.format_exc()}")
    
    try:
        from api.minimal import app
        print("✅ Successfully imported minimal app")
    except Exception as e2:
        print(f"❌ Error importing minimal app: {e2}")
        print(f"Traceback: {traceback.format_exc()}")
        
        # Create fallback app
        app = create_fallback_app()
        print("⚠️ Using fallback app")

# Add error logging for debugging
if app and hasattr(app, 'route'):
    @app.route('/api/debug/import-status')
    def debug_import_status():
        from flask import jsonify
        return jsonify({
            "main_app_imported": import_error is None,
            "import_error": import_error,
            "app_type": "main" if import_error is None else "fallback"
        })

# This is the entry point for Vercel