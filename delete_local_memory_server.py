from qdrant_client import QdrantClient

qdrant = QdrantClient(host="localhost", port=6333)

if qdrant.collection_exists("local_memory"):
    qdrant.delete_collection("local_memory")
    print("🧹 Deleted 'local_memory' collection from server.")
else:
    print("ℹ️ 'local_memory' does not exist on server.")
