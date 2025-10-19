#!/usr/bin/env python3
"""
Simple test script for translation service without external dependencies
"""

import os
import sys

# Add project root to path
project_root = os.path.dirname(__file__)
sys.path.insert(0, project_root)

def load_env_file():
    """Manually load the .env file"""
    env_file = os.path.join(project_root, '.env')
    print(f"Looking for .env file at: {env_file}")
    
    if not os.path.exists(env_file):
        print("❌ .env file not found!")
        return False
    
    try:
        with open(env_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        loaded_vars = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                os.environ[key] = value
                loaded_vars.append(key)
        
        print(f"✅ Loaded {len(loaded_vars)} variables: {', '.join(loaded_vars)}")
        return True
    except Exception as e:
        print(f"❌ Error loading .env file: {e}")
        return False

def test_translation_service():
    print("Testing Translation Service Configuration")
    print("=" * 50)
    
    # Load environment file manually
    load_env_file()
    
    # Test environment variables
    token = os.getenv("GITHUB_AI_TOKEN")
    print(f"\nGITHUB_AI_TOKEN found: {'Yes' if token else 'No'}")
    if token:
        print(f"Token starts with: {token[:20]}...")
    else:
        print("Environment variable GITHUB_AI_TOKEN is not set!")
    
    return bool(token)

if __name__ == "__main__":
    success = test_translation_service()
    if success:
        print("\n✓ Basic configuration looks good")
    else:
        print("\n✗ Configuration issue found")
    exit(0 if success else 1)