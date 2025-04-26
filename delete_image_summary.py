from qdrant_client import QdrantClient

qdrant = QdrantClient(host="localhost", port=6333)

if qdrant.collection_exists("image_summary_memory"):
    qdrant.delete_collection("image_summary_memory")
    print("🧹 Deleted 'image_summary_memory' collection from server.")
else:
    print("ℹ️ 'image_summary_memory' does not exist on server.")
