"""
Diagnostics Script for Local AI Assistant
This script tests each component of your setup to ensure everything is working
"""

import os
import sys
import requests
import subprocess
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

def check_python_version():
    """Check if Python version is compatible"""
    print("\n🔍 Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python version {version.major}.{version.minor} is too old")
        print("   Please use Python 3.8 or newer")
        return False
    else:
        print(f"✅ Python version {version.major}.{version.minor}.{version.micro} is compatible")
        return True

def check_directories():
    """Check if required directories exist"""
    print("\n🔍 Checking directory structure...")
    
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
    
    all_exist = True
    for directory in directories:
        if os.path.exists(directory):
            print(f"✅ Directory exists: {directory}")
        else:
            print(f"❌ Directory missing: {directory}")
            all_exist = False
    
    return all_exist

def check_qdrant():
    """Check if Qdrant is running"""
    print("\n🔍 Checking Qdrant database...")
    try:
        response = requests.get("http://localhost:6333/collections")
        if response.status_code == 200:
            print("✅ Qdrant is running")
            return True
        else:
            print(f"❌ Qdrant returned status code {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to Qdrant")
        print("   Make sure Docker Desktop is running with the Qdrant container")
        return False

def check_lm_studio():
    """Check if LM Studio API is accessible"""
    print("\n🔍 Checking LM Studio API...")
    try:
        response = requests.get("http://127.0.0.1:1234/v1/models")
        if response.status_code == 200:
            print("✅ LM Studio API is accessible")
            if response.json().get("data"):
                print(f"   Available models: {[m['id'] for m in response.json()['data']]}")
            return True
        else:
            print(f"❌ LM Studio API returned status code {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to LM Studio API")
        print("   Make sure LM Studio is running with Local Server enabled (port 1234)")
        return False

def check_embedding_model():
    """Check if sentence transformers can be loaded"""
    print("\n🔍 Checking embedding model...")
    try:
        from sentence_transformers import SentenceTransformer
        model_name = os.getenv("EMBEDDING_MODEL", "BAAI/bge-large-en-v1.5")
        
        print(f"   Loading model: {model_name}")
        start_time = time.time()
        model = SentenceTransformer(model_name)
        load_time = time.time() - start_time
        
        print(f"✅ Embedding model loaded successfully in {load_time:.2f} seconds")
        
        # Test encoding
        test_text = "This is a test sentence to check if encoding works."
        print("   Encoding test sentence...")
        start_time = t