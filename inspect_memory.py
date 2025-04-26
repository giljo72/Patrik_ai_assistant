from qdrant_client import QdrantClient
from pprint import pprint

# === Connect to Qdrant (file-based)
qdrant = QdrantClient(path="F:/qdrant_storage")

# === Collection to inspect
collection = "local_memory"

# === How many results to fetch
limit = 50

print(f"\n🔍 Inspecting contents of: {collection}")
response = qdrant.scroll(
    collection_name=collection,
    limit=limit,
    with_payload=True
)

for i, point in enumerate(response[0], 1):
    payload = point.payload
    print(f"\n[{i}] {payload.get('filename', 'Unknown')}  |  Tag: {payload.get('tag', 'N/A')}")
    print(f"🧠 {payload.get('chunk', '[No text]')[:200]}...")
