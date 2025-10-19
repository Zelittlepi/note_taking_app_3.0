import os
import sys

# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Try to load environment variables
env_loaded = False
try:
    from dotenv import load_dotenv
    load_dotenv()
    env_loaded = True
    print("✅ Environment variables loaded from .env file using python-dotenv")
except ImportError:
    print("python-dotenv not available, trying manual loader")
    try:
        # Manual .env loading
        env_file = os.path.join(os.path.dirname(__file__), '..', '.env')
        if os.path.exists(env_file):
            with open(env_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    os.environ[key] = value
            
            env_loaded = True
            print("✅ Environment variables loaded manually from .env file")
        else:
            print("❌ .env file not found")
    except Exception as e:
        print(f"❌ Manual env loader failed: {e}")
except Exception as e:
    print(f"❌ Error loading .env file: {e}")

# Verify critical environment variables
github_token = os.getenv('GITHUB_AI_TOKEN')
if github_token:
    print(f"✅ GITHUB_AI_TOKEN found (starts with: {github_token[:20]}...)")
else:
    print("❌ GITHUB_AI_TOKEN not found in environment variables")

from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from src.models.user import db
from src.routes.user import user_bp
from src.routes.note import note_bp
from src.models.note import Note

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))

# Use environment variables for configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'asdf#FGSgvasgf$5$WGT')

# Enable CORS for all routes
CORS(app)

app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(note_bp, url_prefix='/api')

# Add health check endpoint
@app.route('/api/health')
def health_check():
    # Check translation service
    translation_available = False
    translation_error = None
    try:
        from src.services.translation import translation_service
        translation_available = translation_service.is_configured()
        if not translation_available:
            translation_error = "Service not configured"
    except Exception as e:
        translation_error = str(e)
    
    return jsonify({
        "status": "ok",
        "message": "NoteTaker API is running",
        "database_configured": bool(os.getenv('DATABASE_URL')),
        "translation_available": translation_available,
        "translation_error": translation_error,
        "github_token_available": bool(os.getenv('GITHUB_AI_TOKEN'))
    })

@app.route('/api/debug/translation')
def debug_translation():
    """Debug endpoint to check translation service status"""
    debug_info = {
        "github_token_available": bool(os.getenv('GITHUB_AI_TOKEN')),
        "openai_import_available": False,
        "translation_service_available": False,
        "translation_service_configured": False,
        "errors": []
    }
    
    # Test OpenAI import
    try:
        import openai
        debug_info["openai_import_available"] = True
    except ImportError as e:
        debug_info["errors"].append(f"OpenAI import failed: {e}")
    
    # Test translation service
    try:
        from src.services.translation import translation_service
        debug_info["translation_service_available"] = True
        debug_info["translation_service_configured"] = translation_service.is_configured()
        
        if translation_service.is_configured():
            # Try a quick translation test
            result = translation_service.translate_to_chinese("test")
            if 'error' in result:
                debug_info["errors"].append(f"Translation test failed: {result['error']}")
            else:
                debug_info["translation_test_success"] = True
                debug_info["translation_test_result"] = result['translated_text']
    except Exception as e:
        debug_info["errors"].append(f"Translation service error: {e}")
    
    return jsonify(debug_info)

# Configure Supabase PostgreSQL database
database_url = os.getenv('DATABASE_URL')
if database_url:
    # Use Supabase PostgreSQL
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    # Fallback to SQLite for local development
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    db.create_all()

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
    # Use environment variables for host and port
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5001))
    debug = os.getenv('FLASK_ENV') == 'development'
    app.run(host=host, port=port, debug=debug)
