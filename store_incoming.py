import os
import shutil
import uuid
from datetime import datetime
from PIL import Image
from docx import Document
from striprtf.striprtf import rtf_to_text
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient, models
import fitz  # PyMuPDF for PDF
import pandas as pd  # For XLSX

# === Paths
incoming_dir = "F:/AI_documents/incoming"
processed_dir = "F:/AI_documents/processed"
subfolders = {
    "text": os.path.join(processed_dir, "text_docs"),
    "spreadsheet": os.path.join(processed_dir, "Spreadsheets"),
    "ppt": os.path.join(processed_dir, "PPT"),
    "image": os.path.join(processed_dir, "Images")
}
log_file_path = os.path.join(processed_dir, "_processing_log.txt")

# === Qdrant + Model
qdrant = QdrantClient(host="localhost", port=6333)
model = SentenceTransformer("BAAI/bge-large-en-v1.5")
print("✅ Embedding model loaded.")

# === Logging
def log_file_entry(filename, tag, summary, project=None):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    summary = summary.strip().replace("\n", " ")[:300]
    project_info = f"Project: {project} | " if project else ""
    
    with open(log_file_path, "a", encoding="utf-8") as f:
        f.write(f"{timestamp} {filename} | {project_info}Tag: {tag} | {summary}\n")

# === Load content file
def load_text(filepath):
    ext = os.path.splitext(filepath)[1].lower()
    try:
        if ext in [".txt", ".md"]:
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read()
        elif ext == ".docx":
            return "\n".join([p.text for p in Document(filepath).paragraphs])
        elif ext == ".rtf":
            with open(filepath, "r", encoding="utf-8") as f:
                return rtf_to_text(f.read())
        elif ext == ".pdf":
            doc = fitz.open(filepath)
            return "\n".join([page.get_text() for page in doc])
        elif ext in [".xlsx", ".xls"]:
            df = pd.read_excel(filepath, sheet_name=None)
            flattened = []
            for name, sheet in df.items():
                flattened.append(f"Sheet: {name}")
                flattened.append(sheet.to_string(index=False))
            return "\n".join(flattened)
        elif ext == ".csv":
            df = pd.read_csv(filepath)
            return df.to_string(index=False)
    except Exception as e:
        print(f"⚠️ Could not load {filepath}: {e}")
    return None

# === Chunking
def chunk_text(text, max_len=512):
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    chunks, current = [], ""
    for line in lines:
        if len(current) + len(line) < max_len:
            current += " " + line
        else:
            chunks.append(current.strip())
            current = line
    if current:
        chunks.append(current.strip())
    return chunks

# === Text Processor
def embed_and_store_text(file_path, tag, target_folder, project=None):
    text = load_text(file_path)
    if not text:
        print(f"⚠️ Skipping unreadable file: {file_path}")
        return

    chunks = chunk_text(text)
    embeddings = model.encode(chunks).tolist()

    if not qdrant.collection_exists("local_memory"):
        qdrant.create_collection(
            collection_name="local_memory",
            vectors_config=models.VectorParams(size=1024, distance=models.Distance.COSINE)
        )

    points = []
    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        payload = {
            "chunk": chunk, 
            "filename": os.path.basename(file_path), 
            "tag": tag
        }
        
        # Add project if available
        if project:
            payload["project"] = project
            
        points.append(
            models.PointStruct(
                id=uuid.uuid4().int >> 64,
                vector=embedding,
                payload=payload
            )
        )
    
    qdrant.upsert(
        collection_name="local_memory",
        points=points
    )

    # Write one-line summary to log (use first chunk)
    first_chunk = chunks[0] if chunks else ""
    summary = " ".join(first_chunk.split()[:50])
    log_file_entry(os.path.basename(file_path), tag, summary, project)

    dest_path = os.path.join(target_folder, os.path.basename(file_path))
    shutil.move(file_path, dest_path)
    print(f"✅ Stored {len(chunks)} chunks from {file_path}")

# === Image archiver
def store_image_metadata(file_path, tag, description=None, project=None):
    print(f"🖼️ Archiving image: {file_path}")
    if not description:
        description = input("📝 Enter a short description of this image (max 50 words): ").strip()
    if not description:
        description = "No description provided."

    vector = model.encode("query: " + description).tolist()

    if not qdrant.collection_exists("image_summary_memory"):
        qdrant.create_collection(
            collection_name="image_summary_memory",
            vectors_config=models.VectorParams(size=1024, distance=models.Distance.COSINE)
        )

    payload = {
        "filename": os.path.basename(file_path), 
        "tag": tag, 
        "summary": description
    }
    
    # Add project if specified
    if project:
        payload["project"] = project
        
    qdrant.upsert(
        collection_name="image_summary_memory",
        points=[
            models.PointStruct(
                id=uuid.uuid4().int >> 64,
                vector=vector,
                payload=payload
            )
        ]
    )

    log_file_entry(os.path.basename(file_path), tag, description, project)
    dest_path = os.path.join(subfolders["image"], os.path.basename(file_path))
    shutil.move(file_path, dest_path)
    print("✅ Image archived with description.")

# === Main loop (when run directly)
if __name__ == "__main__":
    # Ensure directories exist
    for folder in subfolders.values():
        os.makedirs(folder, exist_ok=True)

    for filename in os.listdir(incoming_dir):
        full_path = os.path.join(incoming_dir, filename)
        if not os.path.isfile(full_path):
            continue

        ext = os.path.splitext(filename)[1].lower()
        if ext in [".txt", ".docx", ".md", ".rtf"]:
            print(f"\n📄 Found text file: {filename}")
            tag = input("📌 Tag this as P, B, or PB? ").strip().upper()
            project = input("📂 Add to project (leave blank for none)? ").strip()
            if tag in {"P", "B", "PB"}:
                embed_and_store_text(full_path, tag, subfolders["text"], project if project else None)
        elif ext in [".pdf"]:
            print(f"\n📄 Found PDF file: {filename}")
            tag = input("📌 Tag this PDF as P, B, or PB? ").strip().upper()
            project = input("📂 Add to project (leave blank for none)? ").strip()
            if tag in {"P", "B", "PB"}:
                embed_and_store_text(full_path, tag, subfolders["text"], project if project else None)
        elif ext in [".xls", ".xlsx"]:
            print(f"\n📊 Found spreadsheet file: {filename}")
            tag = input("📌 Tag this spreadsheet as P, B, or PB? ").strip().upper()
            project = input("📂 Add to project (leave blank for none)? ").strip()
            if tag in {"P", "B", "PB"}:
                embed_and_store_text(full_path, tag, subfolders["spreadsheet"], project if project else None)
        elif ext in [".jpg", ".jpeg", ".png", ".bmp", ".gif"]:
            print(f"\n🖼️ Found image file: {filename}")
            tag = input("📌 Tag this image as P, B, or PB? ").strip().upper()
            project = input("📂 Add to project (leave blank for none)? ").strip()
            description = input("📝 Enter a short description of this image (max 50 words): ").strip()
            if tag in {"P", "B", "PB"}:
                store_image_metadata(full_path, tag, description, project if project else None)

    print("\n✅ Finished processing all files.")