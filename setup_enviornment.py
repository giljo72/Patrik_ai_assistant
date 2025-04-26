"""
Environment Setup Script for Local AI Assistant
This script verifies and creates the necessary directory structure
"""

import os
import sys
from dotenv import load_dotenv

def setup_directories():
    """Create all required directories from .env file or use defaults"""
    # Load environment variables
    load_dotenv()
    
    # Define required directories
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
    
    # Create each directory if it doesn't exist
    for directory in directories:
        if directory and not os.path.exists(directory):
            try:
                os.makedirs(directory)
                print(f"✅ Created directory: {directory}")
            except Exception as e:
                print(f"❌ Error creating directory {directory}: {e}")
        else:
            print(f"✓ Directory already exists: {directory}")

def check_dependencies():
    """Check if required Python packages are installed"""
    required_packages = [
        "flask", "qdrant_client", "sentence_transformers", 
        "python-dotenv", "requests", "pillow", "python-docx",
        "striprtf", "pymupdf", "pandas", "torch"
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ Package installed: {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ Missing package: {package}")
    
    if missing_packages:
        print("\n⚠️ Some required packages are missing. Install them with:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    return True

def main():
    print("=" * 60)
    print("Setting up Local AI Assistant Environment")
    print("=" * 60)
    
    # Create directory structure
    print("\n🔍 Setting up directory structure...")
    setup_directories()
    
    # Check dependencies
    print("\n🔍 Checking required Python packages...")
    dependencies_ok = check_dependencies()
    
    # Final status
    print("\n" + "=" * 60)
    if dependencies_ok:
        print("✅ Environment setup complete!")
        print("You can now run your Local AI Assistant")
    else:
        print("⚠️ Environment setup incomplete")
        print("Please install missing packages before continuing")
    print("=" * 60)

if __name__ == "__main__":
    main()