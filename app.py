# === Import section (at the top of the file) ===
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import requests
import json
import os
import time
import uuid
from datetime import datetime
from qdrant_client import QdrantClient, models
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

# Import the RAG manager functions
from rag_manager import generate_rag_response, log_conversation

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", os.urandom(24))
app.template_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Webpage', 'templates')
app.static_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Webpage', 'static')

# === Config ===
PROJECTS_DIR = os.getenv("PROJECTS_DIR", "F:/AI_documents/projects")
CHAT_HISTORY_DIR = os.getenv("CHAT_HISTORY_DIR", "F:/AI_documents/chat_history")
LM_API_URL = os.getenv("LM_API_URL", "http://127.0.0.1:1234/v1/chat/completions")
MODEL_NAME = os.getenv("MODEL_NAME", "llama-3-13b-instruct")
TOP_K = int(os.getenv("TOP_K", 10))
SCORE_THRESHOLD = float(os.getenv("SCORE_THRESHOLD", 0.4))

# Create directories if they don't exist
os.makedirs(PROJECTS_DIR, exist_ok=True)
os.makedirs(CHAT_HISTORY_DIR, exist_ok=True)


# === Load embedding model
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-large-en-v1.5")
embed_model = SentenceTransformer(EMBEDDING_MODEL)
qdrant = QdrantClient(
    host=os.getenv("QDRANT_HOST", "localhost"),
    port=int(os.getenv("QDRANT_PORT", 6333))
)

# === Session management functions
def get_or_create_chat_session():
    """Gets the current chat session or creates a new one"""
    if 'chat_id' not in session:
        session['chat_id'] = str(uuid.uuid4())
        session['chat_history'] = []
        session['current_project'] = None
        session['chat_name'] = f"Chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    return {
        'id': session['chat_id'],
        'history': session['chat_history'],
        'project': session['current_project'],
        'name': session['chat_name']
    }

def save_chat_history(chat_session):
    """Persists chat history to disk"""
    chat_id = chat_session['id']
    history = chat_session['history']
    project = chat_session['project']
    
    # Determine save location based on project
    if project:
        project_dir = os.path.join(PROJECTS_DIR, project)
        os.makedirs(project_dir, exist_ok=True)
        save_path = os.path.join(project_dir, f"{chat_id}.json")
    else:
        save_path = os.path.join(CHAT_HISTORY_DIR, f"{chat_id}.json")
    
    # Save to disk
    with open(save_path, 'w', encoding='utf-8') as f:
        chat_data = {
            'id': chat_id,
            'name': chat_session['name'],
            'project': project,
            'history': history,
            'last_updated': datetime.now().isoformat()
        }
        json.dump(chat_data, f, ensure_ascii=False, indent=2)
    
    return save_path

def load_chat_history(chat_id):
    """Loads a specific chat history"""
    # Look in both locations
    potential_paths = [
        os.path.join(CHAT_HISTORY_DIR, f"{chat_id}.json")
    ]
    
    # Also check all project folders
    for project in os.listdir(PROJECTS_DIR):
        project_path = os.path.join(PROJECTS_DIR, project)
        if os.path.isdir(project_path):
            potential_paths.append(os.path.join(project_path, f"{chat_id}.json"))
    
    # Try to find and load the chat
    for path in potential_paths:
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                chat_data = json.load(f)
                return chat_data
    
    return None

def get_all_chats():
    """Get all chat sessions, both in projects and standalone"""
    chats = []
    
    # Get standalone chats
    for filename in os.listdir(CHAT_HISTORY_DIR):
        if filename.endswith('.json'):
            path = os.path.join(CHAT_HISTORY_DIR, filename)
            with open(path, 'r', encoding='utf-8') as f:
                chat_data = json.load(f)
                chat_data['is_project'] = False
                chats.append(chat_data)
    
    # Get project chats
    for project in os.listdir(PROJECTS_DIR):
        project_path = os.path.join(PROJECTS_DIR, project)
        if os.path.isdir(project_path):
            for filename in os.listdir(project_path):
                if filename.endswith('.json'):
                    path = os.path.join(project_path, filename)
                    with open(path, 'r', encoding='utf-8') as f:
                        chat_data = json.load(f)
                        chat_data['is_project'] = True
                        chat_data['project_name'] = project
                        chats.append(chat_data)
    
    # Sort by last updated time, most recent first
    chats.sort(key=lambda x: x.get('last_updated', ''), reverse=True)
    return chats

def get_all_projects():
    """Get list of all projects"""
    return [d for d in os.listdir(PROJECTS_DIR) if os.path.isdir(os.path.join(PROJECTS_DIR, d))]

# === Routes

@app.route("/")
def index():
    chat_session = get_or_create_chat_session()
    return render_template("index.html", 
                          chat_id=chat_session['id'],
                          chat_name=chat_session['name'],
                          project=chat_session['project'])

@app.route("/chat", methods=["POST"])
def chat():
    # Get current chat session
    chat_session = get_or_create_chat_session()
    
    # Get user input
    user_input = request.json.get("message")
    project_filter = chat_session.get('project')
    
    # Determine profile (business or private) based on current tag preference
    # Default to None if not specified
    tag_preference = session.get('tag_preference')
    profile = None
    if tag_preference == 'B':
        profile = 'business'
    elif tag_preference == 'P':
        profile = 'private'
    
    # Generate response using RAG
    result = generate_rag_response(
        query=user_input,
        chat_history=chat_session['history'],
        project=project_filter,
        profile=profile
    )
    
    # Update chat history
    chat_session['history'].append({"role": "user", "content": user_input})
    chat_session['history'].append({"role": "assistant", "content": result['response']})
    
    # Save updated chat
    save_chat_history(chat_session)
    
    # Log conversation
    log_conversation(
        user_query=user_input,
        assistant_response=result['response'],
        project=project_filter,
        chat_id=chat_session['id']
    )
    
    return jsonify({"response": result['response']})

@app.route("/chat_data")
def get_chat_data():
    """Get chat data for the current session"""
    chat_session = get_or_create_chat_session()
    return jsonify(chat_session)

@app.route("/new_chat", methods=["POST"])
def new_chat():
    # Clear the current session and create a new one
    session.pop('chat_id', None)
    session.pop('chat_history', None)
    session.pop('current_project', None)
    session.pop('chat_name', None)
    
    project = request.json.get("project")
    if project:
        session['current_project'] = project
    
    chat_name = request.json.get("name")
    if chat_name:
        session['chat_name'] = chat_name
    
    chat_session = get_or_create_chat_session()
    save_chat_history(chat_session)
    
    return jsonify({"status": "success", "chat_id": chat_session['id']})

@app.route("/load_chat/<chat_id>")
def load_chat(chat_id):
    chat_data = load_chat_history(chat_id)
    
    if chat_data:
        # Update session with loaded chat
        session['chat_id'] = chat_data['id']
        session['chat_history'] = chat_data['history']
        session['current_project'] = chat_data.get('project')
        session['chat_name'] = chat_data.get('name', f"Chat_{chat_id[:8]}")
        
        return redirect(url_for('index'))
    else:
        return "Chat not found", 404

@app.route("/get_chats")
def get_chats():
    all_chats = get_all_chats()
    return jsonify(all_chats)

@app.route("/get_projects")
def get_projects():
    all_projects = get_all_projects()
    return jsonify(all_projects)

@app.route("/set_chat_name", methods=["POST"])
def set_chat_name():
    new_name = request.json.get("name")
    if new_name:
        chat_session = get_or_create_chat_session()
        chat_session['name'] = new_name
        save_chat_history(chat_session)
        session['chat_name'] = new_name
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "No name provided"}), 400

@app.route("/set_project", methods=["POST"])
def set_project():
    project = request.json.get("project")
    chat_session = get_or_create_chat_session()
    chat_session['project'] = project
    session['current_project'] = project
    save_chat_history(chat_session)
    return jsonify({"status": "success"})

@app.route("/set_tag_preference", methods=["POST"])
def set_tag_preference():
    tag = request.json.get("tag")
    if tag in ['P', 'B', 'PB']:
        session['tag_preference'] = tag
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "Invalid tag"}), 400

# Register file upload blueprint if available
try:
    from file_uploader import file_bp, init_app
    app.register_blueprint(file_bp, url_prefix='/file')
    init_app(app)
    print("✅ File uploader registered")
except ImportError:
    print("⚠️ file_uploader.py not found. File upload functionality disabled.")

if __name__ == "__main__":
    port = int(os.getenv("FLASK_PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "True").lower() == "true"
    app.run(debug=debug, port=port)