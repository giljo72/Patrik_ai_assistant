# store_incoming.py (Updated with full logging and results output)
# Logs summary of all files and writes analysis result for each to a separate file

import os
import re
import uuid
import time
import torch
from PIL import Image
from qdrant_client import QdrantClient, models
from sentence_transformers import SentenceTransformer
from docx import Document
from striprtf.striprtf import rtf_to_text
import clip
import easyocr
from whiteboard_processor import analyze_whiteboard

# === Paths
incoming_dir = "F:/AI_documents/incoming"
processed_dir = "F:/AI_documents/processed"
log_path = os.path.join(incoming_dir, "_processing_log.txt")
result_path = os.path.join(incoming_dir, "_analysis_results.txt")

# === Init
qdrant = QdrantClient(host="localhost", port=6333)
model = SentenceTransformer("BAAI/bge-large-en-v1.5")
clip_model, clip_preprocess = clip.load("ViT-B/32")
reader = easyocr.Reader(['en'], gpu=torch.cuda.is_available())

if torch.cuda.is_available():
    print(f"🚀 GPU: {torch.cuda.get_device_name(0)}")
    print(f"📊 VRAM: {torch.cuda.get_device_properties(0).total_memory / (1024**3):.2f} GB")
    print(f"⚡ CUDA Version: {torch.version.cuda}")

# === Logging

def write_log_entry(filename, tag, summary):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    one_line = summary.split(". ")[0].strip().replace("\n", " ")[:150]
    with open(log_path, "a", encoding="utf-8") as log_file:
        log_file.write(f"[{timestamp}] {filename} | {tag} | {one_line}\n")
    with open(result_path, "a", encoding="utf-8") as out_file:
        out_file.write(f"\n=== Analysis Result: {filename} ({tag}) ===\n[{timestamp}]\n{summary}\n\n")

# === Text file loader and embedder

def load_text(filepath):
    ext = os.path.splitext(filepath)[1].lower()
    try:
        if ext in [".txt", ".md"]:
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read()
        elif ext == ".docx":
            doc = Document(filepath)
            return "\n".join([p.text for p in doc.paragraphs])
        elif ext == ".rtf":
            with open(filepath, "r", encoding="utf-8") as f:
                return rtf_to_text(f.read())
    except Exception as e:
        print(f"⚠️ Could not load {filepath}: {e}")
    return None

def chunk_text(text, max_length=512):
    paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
    chunks, current = [], ""
    for p in paragraphs:
        if len(current) + len(p) < max_length:
            current += " " + p
        else:
            chunks.append(current.strip())
            current = p
    if current:
        chunks.append(current.strip())
    return chunks

def embed_and_store_text(file_path, tag):
    text = load_text(file_path)
    if not text:
        print(f"⚠️ Skipping {file_path}")
        return

    chunks = chunk_text(text)
    embeddings = model.encode(chunks).tolist()
    payloads = [{"chunk": c, "tag": tag, "filename": os.path.basename(file_path)} for c in chunks]

    if not qdrant.collection_exists("local_memory"):
        qdrant.create_collection("local_memory", models.VectorParams(size=1024, distance=models.Distance.COSINE))

    qdrant.upsert("local_memory", [
        models.PointStruct(id=uuid.uuid4().int >> 64, vector=vec, payload=payloads[i])
        for i, vec in enumerate(embeddings)
    ])

    one_line_summary = f"Stored {len(chunks)} text chunks."
    write_log_entry(os.path.basename(file_path), tag, one_line_summary)
    print(f"✅ Stored {len(chunks)} text chunks from: {os.path.basename(file_path)}")

# === Whiteboard/diagram processor

def process_whiteboard_image(file_path, tag):
    print(f"\n🔄 Processing whiteboard image: {os.path.basename(file_path)}")
    result = analyze_whiteboard(file_path, tag)
    summary = result["summary"]

    text_vector = model.encode("passage: " + summary).tolist()

    if not qdrant.collection_exists("image_summary_memory"):
        qdrant.create_collection("image_summary_memory", models.VectorParams(size=1024, distance=models.Distance.COSINE))

    qdrant.upsert("image_summary_memory", [
        models.PointStruct(
            id=int(hash(file_path + "_summary") % (10**10)),
            vector=text_vector,
            payload={
                "filename": os.path.basename(file_path),
                "tag": tag,
                "type": "whiteboard",
                "summary": summary
            }
        )
    ])

    write_log_entry(os.path.basename(file_path), tag, summary)
    print(f"✅ Stored whiteboard summary for: {os.path.basename(file_path)}")

# === Entry loop

for filename in os.listdir(incoming_dir):
    full_path = os.path.join(incoming_dir, filename)
    if not os.path.isfile(full_path):
        continue

    ext = os.path.splitext(filename)[1].lower()
    if ext in [".txt", ".docx", ".md", ".rtf"]:
        print(f"\n📄 Found text file: {filename}")
        tag = input("📌 Tag this as P, B, or PB? ").strip().upper()
        if tag not in {"P", "B", "PB"}:
            print("⚠️ Invalid tag. Skipping file.")
            continue
        embed_and_store_text(full_path, tag)

    elif ext in [".jpg", ".jpeg", ".png", ".bmp", ".gif"]:
        print(f"\n🖼️ Found image file: {filename}")
        tag = input("📌 Tag this image as P, B, or PB? ").strip().upper()
        if tag not in {"P", "B", "PB"}:
            print("⚠️ Invalid tag. Skipping image.")
            continue
        process_whiteboard_image(full_path, tag)

print("\n✅ Done processing incoming folder.")