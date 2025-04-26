"""
File Upload Handler for RAG Assistant
This script provides Flask routes to handle file uploads, tag them, 
and process them into the vector database.
"""

import os
import shutil
import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient, models

# Create blueprint
file_bp = Blueprint('file_upload', __name__)

# Paths
INCOMING_DIR = "F:/AI_documents/incoming"
PROCESSED_DIR = "F:/AI_documents/processed"
LOG_FILE_PATH = os.path.join(PROCESSED_DIR, "_processing_log.txt")

# Ensure directories exist
SUBFOLDERS = {
    "text": os.path.join(PROCESSED_DIR, "text_docs"),
    "spreadsheet": os.path.join(PROCESSED_DIR, "Spreadsheets"),
    "ppt": os.path.join(PROCESSED_DIR, "PPT"),
    "image": os.path.join(PROCESSED_DIR, "Images")
}

for path in [INCOMING_DIR, PROCESSED_DIR] + list(SUBFOLDERS.values()):
    os.makedirs(path, exist_ok=True)

# Load models (will be initialized when blueprint is registered)
embed_model = None
qdrant = None

def init_models():
    """Initialize models - called after app context is available"""
    global embed_model, qdrant
    embed_model = SentenceTransformer("BAAI/bge-large-en-v1.5")
    qdrant = QdrantClient(host="localhost", port=6333)
    print("✅ File uploader models initialized")

def log_file_entry(filename, tag, summary, project=None):
    """Add entry to processing log"""
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    summary = summary.strip().replace("\n", " ")[:300]
    project_info = f"Project: {project} | " if project else ""
    
    with open(LOG_FILE_PATH, "a", encoding="utf-8") as f:
        f.write(f"{timestamp} {filename} | {project_info}Tag: {tag} | {summary}\n")

def get_file_type(filename):
    """Determine file type from extension"""
    ext = os.path.splitext(filename)[1].lower()
    if ext in [".txt", ".md", ".docx", ".rtf", ".pdf"]:
        return "text"
    elif ext in [".xlsx", ".xls", ".csv"]:
        return "spreadsheet"
    elif ext in [".pptx", ".ppt"]:
        return "ppt"
    elif ext in [".jpg", ".jpeg", ".png", ".bmp", ".gif"]:
        return "image"
    else:
        return "other"

@file_bp.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload from the web interface"""
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "No file part"}), 400
    
    file = request.files['file']
    tag = request.form.get('tag', '').upper()
    project = request.form.get('project', '')
    description = request.form.get('description', '')
    
    if file.filename == '':
        return jsonify({"status": "error", "message": "No file selected"}), 400
    
    if tag not in ['P', 'B', 'PB']:
        return jsonify({"status": "error", "message": "Invalid tag. Use P, B, or PB"}), 400
    
    # Save file to incoming directory
    filename = secure_filename(file.filename)
    save_path = os.path.join(INCOMING_DIR, filename)
    file.save(save_path)
    
    # Queue for processing
    process_file(save_path, tag, project, description)
    
    return jsonify({
        "status": "success", 
        "message": f"File {filename} uploaded and queued for processing",
        "filename": filename
    })

def process_file(file_path, tag, project=None, description=None):
    """Process a file by embedding it and storing in Qdrant"""
    filename = os.path.basename(file_path)
    file_type = get_file_type(filename)
    
    # Generate initial summary
    auto_summary = f"File uploaded: {filename}"
    if description:
        auto_summary = description
    
    # Log the upload
    log_file_entry(filename, tag, auto_summary, project)
    
    # Determine destination folder
    dest_folder = SUBFOLDERS.get(file_type, PROCESSED_DIR)
    dest_path = os.path.join(dest_folder, filename)
    
    if file_type == "text":
        # Process text file with your existing code from store_incoming.py
        from store_incoming import embed_and_store_text
        embed_and_store_text(file_path, tag, dest_folder, project=project)
    elif file_type == "spreadsheet":
        # Process spreadsheet (can be implemented similar to text)
        from store_incoming import embed_and_store_text
        embed_and_store_text(file_path, tag, dest_folder, project=project)
    elif file_type == "image":
        # For images, store the description
        if description:
            vector = embed_model.encode("query: " + description).tolist()
            
            if not qdrant.collection_exists("image_summary_memory"):
                qdrant.create_collection(
                    collection_name="image_summary_memory",
                    vectors_config=models.VectorParams(size=len(vector), distance=models.Distance.COSINE)
                )
            
            qdrant.upsert(
                collection_name="image_summary_memory",
                points=[
                    models.PointStruct(
                        id=uuid.uuid4().int >> 64,
                        vector=vector,
                        payload={
                            "filename": filename, 
                            "tag": tag,
                            "project": project,
                            "summary": description
                        }
                    )
                ]
            )
        
        # Move file to destination
        shutil.move(file_path, dest_path)
    else:
        # Just move other file types
        shutil.move(file_path, dest_path)
    
    return True

# Register with app
def init_app(app):
    app.register_blueprint(file_bp, url_prefix='/file', name='file_uploader_blueprint')
    with app.app_context():
        init_models()