import os
import torch
from sentence_transformers import SentenceTransformer, util
from qdrant_client import QdrantClient, models

# === Config ===
collection_name = "image_summary_memory"
tag_to_search = "PB"  # Change as needed

# === Load embedding model
text_model = SentenceTransformer('BAAI/bge-base-en-v1.5')

# === Get user query
query = input("🔍 Enter your image memory question: ")

# === Get embedding for semantic search
query_vector = text_model.encode("query: " + query).tolist()

# === Connect to Qdrant
qdrant = QdrantClient(host="localhost", port=6333, timeout=30.0)

# === Build filter by tag
filter_condition = models.Filter(
    must=[
        models.FieldCondition(
            key="tag",
            match=models.MatchValue(value=tag_to_search)
        )
    ]
)

# === Query top 5 results
response = qdrant.query_points(
    collection_name=collection_name,
    query=query_vector,
    limit=5,
    with_payload=True,
    query_filter=filter_condition
).points

# === Show results
print("\n🖼️ Top Image Matches:")
for r in response:
    caption = r.payload.get("caption", "")
    filename = r.payload.get("filename", "Unknown")
    print(f"🔹 Score: {r.score:.4f} | File: {filename}")
    print(f"   📝 Caption: {caption}\n")
