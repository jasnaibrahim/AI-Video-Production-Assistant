#!/usr/bin/env python3
"""
AI Video Production Assistant - Startup Script
Run this to start both the FastAPI backend and Streamlit frontend
"""

import subprocess
import sys
import time
import threading
import os
from pathlib import Path

def check_requirements():
    """Check if all required packages are installed"""
    try:
        import fastapi
        import streamlit
        import openai
        import uvicorn
        print("✅ All required packages are installed!")
        return True
    except ImportError as e:
        print(f"❌ Missing package: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def check_env_file():
    """Check if .env file exists and has OpenAI API key"""
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found!")
        print("Please create a .env file with your OpenAI API key:")
        print("OPENAI_API_KEY=your_api_key_here")
        return False
    
    with open(env_file, 'r') as f:
        content = f.read()
        if "OPENAI_API_KEY" not in content:
            print("❌ OPENAI_API_KEY not found in .env file!")
            return False
    
    print("✅ Environment file configured!")
    return True

def start_fastapi():
    """Start the FastAPI backend"""
    print("🚀 Starting FastAPI backend on http://localhost:8000")
    subprocess.run([
        sys.executable, "-m", "uvicorn", 
        "main:app", 
        "--host", "0.0.0.0", 
        "--port", "8000",
        "--reload"
    ])

def start_streamlit():
    """Start the Streamlit frontend"""
    print("🎬 Starting Streamlit frontend on http://localhost:8501")
    time.sleep(3)  # Wait for FastAPI to start
    subprocess.run([
        sys.executable, "-m", "streamlit", 
        "run", "streamlit_app.py",
        "--server.port", "8501",
        "--server.address", "0.0.0.0"
    ])

def main():
    """Main function to start the application"""
    print("🎬 AI Video Production Assistant")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Check environment
    if not check_env_file():
        sys.exit(1)
    
    print("\n🚀 Starting application...")
    print("FastAPI Backend: http://localhost:8000")
    print("Streamlit Frontend: http://localhost:8501")
    print("\nPress Ctrl+C to stop both services")
    print("=" * 50)
    
    try:
        # Start FastAPI in a separate thread
        fastapi_thread = threading.Thread(target=start_fastapi, daemon=True)
        fastapi_thread.start()
        
        # Start Streamlit in main thread
        start_streamlit()
        
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down services...")
        print("Thanks for using AI Video Production Assistant!")

if __name__ == "__main__":
    main()
