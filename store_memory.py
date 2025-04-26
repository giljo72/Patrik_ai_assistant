import os
import hashlib
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct
from document_loader import load_text_from_file
from sentence_transformers import SentenceTransformer

# === Load your document ===
file_path = "F:\\AI_documents\\incoming\\sample_test.txt"
text = load_text_from_file(file_path)

# === Load local BGE embedding model ===
model = SentenceTransformer('BAAI/bge-base-en-v1.5')

# === Create embedding ===
# BGE recommends using a "query: " or "passage: " prefix
embedding = model.encode("passage: " + text[:1000])  # Limit to 1000 chars for safety

# === Connect to Qdrant ===
qdrant = QdrantClient(host="localhost", port=6333)

# === Create collection if not exists ===
collection_name = "local_memory"
if collection_name not in [c.name for c in qdrant.get_collections().collections]:
    qdrant.recreate_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=len(embedding), distance=Distance.COSINE)
    )

# === Create and upsert a point ===
qdrant.upsert(
    collection_name=collection_name,
    points=[
        PointStruct(
            id=int(hashlib.md5(file_path.encode()).hexdigest(), 16) % (10 ** 12),
            vector=embedding.tolist(),
            payload={
                "filename": os.path.basename(file_path),
                "tag": "personal"
            }
        )
    ]
)

print("✅ Document embedded with BGE and stored in Qdrant!")
