import os
import hashlib
import nltk
import tiktoken
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct
from document_loader import load_text_from_file
from sentence_transformers import SentenceTransformer

# === Config ===
file_path = "F:\\AI_documents\\incoming\\sample_test.txt"
collection_name = "local_memory"
chunk_token_limit = 400

# === Load and preprocess ===
text = load_text_from_file(file_path)
sentences = nltk.sent_tokenize(text)

# === Tokenizer ===
tokenizer = tiktoken.get_encoding("cl100k_base")  # Same tokenizer used by OpenAI & many LLMs

def num_tokens(text):
    return len(tokenizer.encode(text))

# Set this to "P", "B", or "PB" depending on the file type
doc_tag = "P"  # <-- Change this per document

# === Sentence-aware token-limited chunking ===
chunks = []
current_chunk = []
token_count = 0

for sentence in sentences:
    sentence_tokens = num_tokens(sentence)
    if token_count + sentence_tokens > chunk_token_limit:
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        current_chunk = [sentence]
        token_count = sentence_tokens
    else:
        current_chunk.append(sentence)
        token_count += sentence_tokens

if current_chunk:
    chunks.append(" ".join(current_chunk))

print(f"📄 Split into {len(chunks)} smart chunks.")

# === Embed & store chunks ===
model = SentenceTransformer('BAAI/bge-base-en-v1.5')
qdrant = QdrantClient(
    host="localhost",
    port=6333,
    timeout=30.0,
    prefer_grpc=False,  # Force REST to avoid silent gRPC fallback
    api_key=None,       # Just explicit if needed later
    https=False,        # Make sure we aren't accidentally using HTTPS
)

# Create collection if needed
if collection_name not in [c.name for c in qdrant.get_collections().collections]:
    qdrant.recreate_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(
            size=model.get_sentence_embedding_dimension(),
            distance=Distance.COSINE
        )
    )

# Prepare points
points = []
for i, chunk in enumerate(chunks):
    embedding = model.encode("passage: " + chunk)
    point = PointStruct(
        id=int(hashlib.md5(f"{file_path}_{i}".encode()).hexdigest(), 16) % (10 ** 12),
        vector=embedding.tolist(),
        payload={
            "chunk": chunk,
            "filename": os.path.basename(file_path),
            "tag": doc_tag,
            "chunk_index": i
        }
    )
    points.append(point)

# Upload to Qdrant
print(f"🔁 Attempting to upload {len(points)} chunks to Qdrant...")
try:
    qdrant.upsert(collection_name=collection_name, points=points)
    print(f"✅ Stored {len(points)} intelligently chunked segments in Qdrant.")
except Exception as e:
    print("❌ Failed to upsert into Qdrant.")
    print(f"🔎 Error: {type(e).__name__}: {e}")
print(f"✅ Stored {len(points)} intelligently chunked segments in Qdrant.")
