from qdrant_client import QdrantClient

qdrant = QdrantClient(host="localhost", port=6333)

print("🔍 Inspecting 'image_summary_memory'...")

response = qdrant.scroll(
    collection_name="image_summary_memory",
    with_payload=True,
    limit=100
)

for i, pt in enumerate(response[0], 1):
    payload = pt.payload
    print(f"\n[{i}] {payload.get('filename', 'Unknown')}  |  Tag: {payload.get('tag', 'N/A')}")
    print(f"🧠 Summary:\n{payload.get('summary', '[No summary found]')[:500]}...")
