"""
RAG Manager for Local AI Assistant
This script handles the interaction between the LLM and the vector database,
implementing Retrieval Augmented Generation for the chatbot.
"""

import os
import requests
import json
from datetime import datetime
from qdrant_client import QdrantClient, models
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# === Configuration ===
LM_API_URL = os.getenv("LM_API_URL", "http://127.0.0.1:1234/v1/chat/completions")
MODEL_NAME = os.getenv("MODEL_NAME", "llama-3-13b-instruct")
TOP_K = int(os.getenv("TOP_K", 10))
SCORE_THRESHOLD = float(os.getenv("SCORE_THRESHOLD", 0.4))
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-large-en-v1.5")

# Initialize clients and models
embed_model = SentenceTransformer(EMBEDDING_MODEL)
qdrant = QdrantClient(
    host=os.getenv("QDRANT_HOST", "localhost"),
    port=int(os.getenv("QDRANT_PORT", 6333))
)

def retrieve_memory_context(query, project_filter=None, tag_filter=None):
    """Retrieve relevant memory context based on query similarity"""
    query_vector = embed_model.encode(query).tolist()
    
    def search_memory(collection):
        try:
            # Build filter conditions if needed
            filter_conditions = []
            if project_filter:
                filter_conditions.append(
                    models.FieldCondition(
                        key="project",
                        match=models.MatchValue(value=project_filter)
                    )
                )
            if tag_filter:
                filter_conditions.append(
                    models.FieldCondition(
                        key="tag",
                        match=models.MatchValue(value=tag_filter)
                    )
                )
                
            # Apply filter if conditions exist
            query_filter = None
            if filter_conditions:
                query_filter = models.Filter(
                    must=filter_conditions
                )
            
            response = qdrant.query_points(
                collection_name=collection,
                query=query_vector,
                limit=TOP_K,
                with_payload=True,
                query_filter=query_filter
            )
            
            results = []
            for point in response.points:
                score = point.score
                if score >= SCORE_THRESHOLD:
                    payload = point.payload
                    text = payload.get('chunk') or payload.get('summary')
                    if text:
                        results.append({
                            'score': score,
                            'text': text.strip(),
                            'filename': payload.get('filename', 'Unknown'),
                            'tag': payload.get('tag', 'N/A'),
                            'collection': collection,
                            'project': payload.get('project', 'General')
                        })
            return results
        except Exception as e:
            print(f"⚠️ Qdrant error: {e}")
            return []

    # Search both text and image collections
    text_mem = search_memory("local_memory")
    img_mem = search_memory("image_summary_memory")

    # Combine and sort by relevance score
    combined = sorted(text_mem + img_mem, key=lambda x: x['score'], reverse=True)
    
    # Format context with metadata
    context_lines = []
    for item in combined[:TOP_K]:
        source_info = f"{item['filename']} [{item['tag']}]"
        confidence = round(item['score'] * 100)
        context_lines.append(f"SOURCE: {source_info} (Confidence: {confidence}%)\nCONTENT: {item['text']}")
    
    if not context_lines:
        return "No relevant information found in memory."
    
    return "\n\n".join(context_lines)

def build_system_prompt(project=None, profile=None):
    """Build system prompt based on project and profile context"""
    base_prompt = """You are a helpful AI assistant with access to the user's document memory.
When answering questions, use relevant information from the memory context provided.
If the asked information is not in the context, admit that you don't know or suggest
that the user upload relevant documents to help you better assist them."""

    # Add project context if available
    if project:
        base_prompt += f"\n\nCurrent Project Context: {project}"
        base_prompt += f"\nWhen helping with this project, prioritize information from documents tagged with this project."
    
    # Add profile context
    if profile == "business":
        base_prompt += """
        
Business Profile Guidelines:
- Maintain professional tone and focus on business objectives
- Prioritize actionable insights and strategic recommendations
- When analyzing documents, focus on commercial implications, ROI, and market positioning
- Present information in structured, concise formats suitable for business contexts
"""
    elif profile == "private":
        base_prompt += """
        
Private Profile Guidelines:
- Use a more conversational, personalized tone
- When analyzing personal documents, focus on the user's stated goals and preferences
- Respect privacy and maintain confidentiality in all discussions
- Present information in an accessible, user-friendly manner
"""
    
    return base_prompt

def query_llm(messages, temperature=0.7, top_p=0.9):
    """Send a query to the LLM and return the response"""
    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "temperature": temperature,
        "top_p": top_p
    }
    
    try:
        response = requests.post(LM_API_URL, json=payload, timeout=60)
        response.raise_for_status()  # Raise exception for bad status codes
        result = response.json()
        return result["choices"][0]["message"]["content"].strip()
    except requests.exceptions.RequestException as e:
        print(f"⚠️ LLM API error: {e}")
        return f"I encountered an error when trying to process your request. Please check that LM Studio is running with model '{MODEL_NAME}'. Error: {str(e)}"

def generate_rag_response(query, chat_history=None, project=None, profile=None, tag_filter=None):
    """Generate a response using RAG methodology"""
    # Retrieve relevant context
    memory_context = retrieve_memory_context(query, project_filter=project, tag_filter=tag_filter)
    
    # Build messages array for the LLM API
    messages = [
        {"role": "system", "content": build_system_prompt(project, profile)}
    ]
    
    # Add chat history if available
    if chat_history:
        for entry in chat_history:
            messages.append({"role": entry["role"], "content": entry["content"]})
    
    # Add memory context and current query
    context_message = f"""
Memory context relevant to the question is below:

===== MEMORY CONTEXT START =====
{memory_context}
===== MEMORY CONTEXT END =====

The user's question is: {query}

Answer based on the provided memory context when relevant. If the answer isn't in the context, say so clearly.
"""
    
    messages.append({"role": "user", "content": context_message})
    
    # Query the LLM
    response = query_llm(messages)
    
    return {
        "response": response,
        "context_used": memory_context,
        "timestamp": datetime.now().isoformat()
    }

def log_conversation(user_query, assistant_response, project=None, chat_id=None):
    """Log the conversation for future reference"""
    log_dir = os.getenv("CHAT_HISTORY_DIR", "F:/AI_documents/chat_history")
    os.makedirs(log_dir, exist_ok=True)
    
    # Determine file path based on project and chat ID
    if project:
        project_dir = os.path.join(os.getenv("PROJECTS_DIR", "F:/AI_documents/projects"), project)
        os.makedirs(project_dir, exist_ok=True)
        log_path = os.path.join(project_dir, f"chat_{chat_id or 'latest'}.log")
    else:
        log_path = os.path.join(log_dir, f"chat_{chat_id or 'latest'}.log")
    
    # Append to log file
    with open(log_path, "a", encoding="utf-8") as f:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] USER: {user_query}\n")
        f.write(f"[{timestamp}] ASSISTANT: {assistant_response}\n\n")