"""
Startup script for the Local AI Assistant
This script ensures all components are initialized in the correct order
"""

import os
import sys
import subprocess
import time
import requests
from dotenv import load_dotenv

def check_qdrant():
    """Check if Qdrant is running"""
    try:
        response = requests.get("http://localhost:6333/collections")
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        return False

def check_lm_studio():
    """Check if LM Studio API is accessible"""
    try:
        response = requests.get("http://127.0.0.1:1234/v1/models")
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        return False

def create_required_directories():
    """Create all required directories from .env file"""
    load_dotenv()
    
    directories = [
        os.getenv("INCOMING_DIR", "F:/AI_documents/incoming"),
        os.getenv("PROCESSED_DIR", "F:/AI_documents/processed"),
        os.getenv("PROJECTS_DIR", "F:/AI_documents/projects"),
        os.getenv("CHAT_HISTORY_DIR", "F:/AI_documents/chat_history"),
        os.getenv("TEXT_DOCS_DIR", "F:/AI_documents/processed/text_docs"),
        os.getenv("SPREADSHEETS_DIR", "F:/AI_documents/processed/Spreadsheets"),
        os.getenv("PPT_DIR", "F:/AI_documents/processed/PPT"),
        os.getenv("IMAGES_DIR", "F:/AI_documents/processed/Images")
    ]
    
    for directory in directories:
        if directory and not os.path.exists(directory):
            os.makedirs(directory, ensure_ascii=False)
            print(f"✅ Created directory: {directory}")

def main():
    print("=" * 60)
    print("Starting Local AI Assistant")
    print("=" * 60)
    
    # Create required directories
    print("\n🔍 Checking required directories...")
    create_required_directories()
    
    # Check if Qdrant is running
    print("\n🔍 Checking Qdrant database...")
    if not check_qdrant():
        print("❌ Qdrant does not appear to be running!")
        print("Please make sure Docker Desktop is running with the Qdrant container")
        choice = input("Continue anyway? (y/n): ").lower()
        if choice != 'y':
            print("Exiting. Please start Qdrant and try again.")
            sys.exit(1)
    else:
        print("✅ Qdrant is running")
    
    # Check if LM Studio is running
    print("\n🔍 Checking LM Studio API...")
    if not check_lm_studio():
        print("❌ LM Studio API does not appear to be accessible!")
        print("Please make sure LM Studio is running with:")
        print("  1. A model loaded")
        print("  2. Local Server enabled in settings (port 1234)")
        choice = input("Continue anyway? (y/n): ").lower()
        if choice != 'y':
            print("Exiting. Please start LM Studio and try again.")
            sys.exit(1)
    else:
        print("✅ LM Studio API is accessible")
    
    # Run the test script
    print("\n🔍 Testing LLM connection...")
    try:
        subprocess.run([sys.executable, "test_llm_connection.py"], check=True)
    except subprocess.CalledProcessError:
        print("❌ LLM connection test failed!")
        choice = input("Continue anyway? (y/n): ").lower()
        if choice != 'y':
            print("Exiting. Please check your LLM setup and try again.")
            sys.exit(1)
    
    # Start the Flask app
    print("\n🚀 Starting Flask application...")
    try:
        # Use subprocess to run and stay alive even if this script is closed
        subprocess.Popen([sys.executable, "app.py"])
        
        # Give Flask a moment to start
        time.sleep(2)
        
        # Try to connect to verify it's running
        try:
            response = requests.get("http://localhost:5000/")
            if response.status_code == 200:
                print("✅ Flask app started successfully!")
                print("\n🌐 Access your assistant at http://localhost:5000")
            else:
                print(f"⚠️ Flask app may have started but returned status code {response.status_code}")
        except requests.exceptions.ConnectionError:
            print("⚠️ Flask app may have started but isn't responding to requests yet")
            print("Try accessing http://localhost:5000 in your browser")
    
    except Exception as e:
        print(f"❌ Error starting Flask app: {e}")
        sys.exit(1)
    
    print("\n✨ System startup complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()