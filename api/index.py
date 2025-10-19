import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Try to import the main app, fallback to minimal version
try:
    from src.main import app
    print("Successfully imported main app")
except Exception as e:
    print(f"Error importing main app: {e}, using minimal version")
    try:
        from api.minimal import app
        print("Successfully imported minimal app")
    except Exception as e2:
        print(f"Error importing minimal app: {e2}")
        # Last resort fallback
        from flask import Flask, jsonify
        app = Flask(__name__)
        
        @app.route('/api/health')
        def health():
            return jsonify({
                "status": "error", 
                "message": f"Both main and minimal app import failed. Main: {str(e)}, Minimal: {str(e2)}"
            })
        
        @app.route('/')
        def index():
            return jsonify({
                "message": "NoteTaker API - Import Error",
                "error": f"Main: {str(e)}, Minimal: {str(e2)}"
            })

# This is the entry point for Vercel