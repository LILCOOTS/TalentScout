#!/usr/bin/env python3
"""
TalentScout Hiring Assistant Startup Script
"""

import sys
import os
import subprocess

def check_python_version():
    """Check if Python version is 3.8 or higher."""
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required.")
        print(f"Current version: {sys.version}")
        return False
    return True

def check_dependencies():
    """Check if required packages are installed."""
    try:
        import streamlit
        import google.generativeai
        import dotenv
        print("✓ All dependencies are installed.")
        return True
    except ImportError as e:
        print(f"Error: Missing dependency - {e}")
        print("Run: pip install -r requirements.txt")
        return False

def check_env_file():
    """Check if .env file exists and has required variables."""
    if not os.path.exists('.env'):
        print("Warning: .env file not found.")
        print("Copy .env.example to .env and add your Gemini API key.")
        return False
    
    # Check for GEMINI_API_KEY
    with open('.env', 'r') as f:
        content = f.read()
        if 'GEMINI_API_KEY=' in content and 'your_gemini_api_key_here' not in content:
            print("✓ Environment file configured.")
            return True
    
    print("Warning: Please set your GEMINI_API_KEY in the .env file.")
    return False

def main():
    """Main startup function."""
    print("🎯 TalentScout Hiring Assistant")
    print("=" * 40)
    
    # Check prerequisites
    if not check_python_version():
        return 1
    
    if not check_dependencies():
        return 1
    
    env_ok = check_env_file()
    
    print("\nStarting Streamlit application...")
    
    try:
        # Run Streamlit app
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error starting application: {e}")
        return 1
    except KeyboardInterrupt:
        print("\nApplication stopped by user.")
        return 0
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
