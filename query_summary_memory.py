from qdrant_client import QdrantClient, models
from sentence_transformers import SentenceTransformer

# === Config
collection_name = "image_summary_memory"
tag = "PB"
query = input("🔍 Enter your question about a stored whiteboard: ")

# === Load embedding model
model = SentenceTransformer("BAAI/bge-base-en-v1.5")
query_vector = model.encode("query: " + query)

# === Connect to Qdrant
qdrant = QdrantClient(host="localhost", port=6333, timeout=30.0)

# === Build tag filter
filter_condition = models.Filter(
    must=[
        models.FieldCondition(
            key="tag",
            match=models.MatchValue(value=tag)
        )
    ]
)

# === Query Qdrant
response = qdrant.query_points(
    collection_name=collection_name,
    query=query_vector.tolist(),
    limit=5,
    with_payload=True,
    query_filter=filter_condition
)

# === Display results
print("\n📄 Top Memory Matches:")
for point in response.points:
    print(f"🔹 Score: {point.score:.4f} | File: {point.payload.get('filename')}")
    print(f"📝 Summary:\n{point.payload.get('summary')}\n")
