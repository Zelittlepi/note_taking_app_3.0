"""
Manual environment loader for when python-dotenv is not available
"""
import os

def load_env_manual(env_file_path=None):
    """Manually load environment variables from .env file"""
    if env_file_path is None:
        # Look for .env file in project root
        current_dir = os.path.dirname(__file__)
        env_file_path = os.path.join(os.path.dirname(current_dir), '.env')
    
    if not os.path.exists(env_file_path):
        print(f"No .env file found at {env_file_path}")
        return False
    
    try:
        with open(env_file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                # Remove quotes if present
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                elif value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]
                os.environ[key] = value
        
        print(f"Successfully loaded environment variables from {env_file_path}")
        return True
    except Exception as e:
        print(f"Error reading .env file: {e}")
        return False

# Auto-load when imported
if __name__ != "__main__":
    load_env_manual()