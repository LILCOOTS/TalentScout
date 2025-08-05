"""
Vercel-compatible entry point for TalentScout Streamlit app
"""
import streamlit as st
from streamlit.web import cli as stcli
import sys
import os

def main():
    """Main function to run Streamlit app"""
    # Add current directory to path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)
    
    # Import the main app
    import app
    
if __name__ == "__main__":
    main()
