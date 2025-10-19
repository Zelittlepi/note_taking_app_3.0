#!/usr/bin/env python3
"""
Deployment test script for the NoteTaker application
"""

import sys
import os

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    
    try:
        import flask
        print("✓ Flask imported successfully")
    except ImportError as e:
        print(f"✗ Flask import failed: {e}")
        return False
    
    try:
        import flask_sqlalchemy
        print("✓ Flask-SQLAlchemy imported successfully")
    except ImportError as e:
        print(f"✗ Flask-SQLAlchemy import failed: {e}")
        return False
    
    try:
        import psycopg2
        print("✓ psycopg2 imported successfully")
    except ImportError as e:
        print(f"✗ psycopg2 import failed: {e}")
        return False
    
    try:
        import openai
        print("✓ OpenAI imported successfully")
    except ImportError as e:
        print(f"✗ OpenAI import failed: {e}")
        print("  This is optional - translation features will be disabled")
    
    try:
        import dotenv
        print("✓ python-dotenv imported successfully")
    except ImportError as e:
        print(f"✗ python-dotenv import failed: {e}")
        print("  This is optional - using os.environ instead")
    
    return True

def test_app_creation():
    """Test if the Flask app can be created"""
    print("\nTesting app creation...")
    
    try:
        # Add project root to path
        project_root = os.path.dirname(os.path.dirname(__file__))
        sys.path.insert(0, project_root)
        
        from src.main import app
        print("✓ Flask app created successfully")
        return True
    except Exception as e:
        print(f"✗ App creation failed: {e}")
        return False

def main():
    print("NoteTaker Deployment Test")
    print("=" * 40)
    
    if not test_imports():
        print("\n❌ Import tests failed")
        return 1
    
    if not test_app_creation():
        print("\n❌ App creation test failed")
        return 1
    
    print("\n✅ All tests passed! Ready for deployment.")
    return 0

if __name__ == "__main__":
    sys.exit(main())