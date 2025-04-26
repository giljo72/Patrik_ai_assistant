"""
Script to test LLM connection with LM Studio
Run this script to verify your LM Studio connection is working properly
"""

import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# LM Studio API settings
LM_API_URL = os.getenv("LM_API_URL", "http://127.0.0.1:1234/v1/chat/completions")
MODEL_NAME = os.getenv("MODEL_NAME", "llama-3-13b-instruct")

def test_llm_connection():
    """Test connection to LM Studio API"""
    print(f"Testing connection to LM Studio at {LM_API_URL}")
    print(f"Using model: {MODEL_NAME}")
    
    # Simple test message
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello! Can you confirm that you're receiving my messages?"}
    ]
    
    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "temperature": 0.7,
        "top_p": 0.9
    }
    
    try:
        print("Sending test request...")
        response = requests.post(LM_API_URL, json=payload, timeout=30)
        
        # Check status code
        if response.status_code != 200:
            print(f"❌ Error: Received status code {response.status_code}")
            print(f"Response content: {response.text}")
            return False
        
        # Parse response
        result = response.json()
        if "choices" in result and len(result["choices"]) > 0:
            response_text = result["choices"][0]["message"]["content"]
            print(f"\n✅ Connection successful!")
            print(f"\nResponse from LLM:\n{'-' * 50}\n{response_text}\n{'-' * 50}")
            return True
        else:
            print(f"❌ Error: Unexpected response format")
            print(f"Response: {json.dumps(result, indent=2)}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error: Could not connect to LM Studio API")
        print("Please make sure LM Studio is running and the API server is enabled")
        print("In LM Studio, check that 'Local Server' is enabled in settings")
        return False
    except requests.exceptions.Timeout:
        print("❌ Timeout error: The request took too long to complete")
        print("This could mean the model is still loading or your GPU/CPU is under heavy load")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {type(e).__name__}: {e}")
        return False

def test_rag_functionality():
    """Test RAG functionality if LLM connection works"""
    print("\nTesting RAG functionality...")
    
    try:
        from rag_manager import generate_rag_response
        
        test_query = "What capabilities does this assistant have?"
        
        print(f"Sending test RAG query: '{test_query}'")
        result = generate_rag_response(test_query)
        
        print(f"\n✅ RAG functionality test successful!")
        print(f"\nResponse from RAG:\n{'-' * 50}\n{result['response']}\n{'-' * 50}")
        return True
    except Exception as e:
        print(f"❌ RAG test error: {type(e).__name__}: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("LM Studio Connection Test")
    print("=" * 50)
    
    # First test LLM connection
    if test_llm_connection():
        # If successful, also test RAG
        test_rag_functionality()
    
    print("\nTest completed.")