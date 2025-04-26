from qdrant_client import QdrantClient

qdrant = QdrantClient(path="F:/qdrant_storage")

for name in ["local_memory", "image_summary_memory"]:
    if qdrant.collection_exists(name):
        qdrant.delete_collection(name)
        print(f"🧹 Deleted collection: {name}")
    else:
        print(f"ℹ️ Collection not found: {name}")
