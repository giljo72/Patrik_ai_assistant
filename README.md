# Local AI Assistant

A private, local AI assistant with RAG capabilities, document management, and chat history.

## Features

- Local LLM powered by LM Studio (Llama 3)
- Vector database storage using Qdrant
- Document processing for various file types (PDF, DOCX, TXT, XLSX, etc.)
- Image processing for whiteboard sessions
- Web interface for chatting and file management
- Project-based organization
- Profile-based context (Business/Private)

## Directory Structure
F:/
├── Project_Files/           # Main project code
│   ├── app.py               # Main Flask application
│   ├── rag_manager.py       # RAG implementation
│   ├── file_uploader.py     # File upload handling
│   ├── document_loader.py   # Document processing
│   ├── store_incoming.py    # File ingestion
│   ├── Webpage/             # Web interface
│   │   ├── templates/       # HTML templates
│   │   ├── static/          # CSS, JS, images
│   └── ...
├── AI_documents/            # Document storage
│   ├── incoming/            # Newly uploaded files
│   ├── processed/           # Processed files
│   │   ├── text_docs/       # Text documents
│   │   ├── Spreadsheets/    # Spreadsheets
│   │   ├── PPT/             # Presentations
│   │   ├── Images/          # Images
│   │   └── _processing_log.txt
│   ├── projects/            # Project-specific files
│   └── chat_history/        # Chat logs
└── qdrant_storage/          # Vector database files

## Setup

1. Install required packages:
pip install -r requirements.txt

2. Set up the environment:
python setup_environment.py

3. Start the Docker container for Qdrant:
docker run -d -p 6333:6333 -v F:/qdrant_storage:/qdrant/storage qdrant/qdrant

4. Launch LM Studio and enable the local server on port 1234

5. Start the application:
python app.py

6. Access the web interface at http://localhost:5000

## Development

- `run_assistant.py` - Launch all components in the correct order
- `test_llm_connection.py` - Test the connection to LM Studio
- `delete_local_memory_server.py` - Reset the vector database

## Tags

- P - Private content
- B - Business content
- PB - Content for both contexts