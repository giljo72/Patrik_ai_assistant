import os
from qdrant_client import QdrantClient, models
from sentence_transformers import SentenceTransformer
import clip
import torch

# === Load models
text_model = SentenceTransformer('BAAI/bge-large-en-v1.5')
print("✅ Text embedding model loaded: bge-large-en-v1.5")
clip_model, clip_preprocess = clip.load("ViT-B/32")
print("✅ CLIP model loaded")
device = "cuda" if torch.cuda.is_available() else "cpu"
clip_model.to(device)

# === User query input
query = input("🔍 Enter your memory question: ")

# === Encode query for each modality
text_vector = text_model.encode("query: " + query).tolist()
with torch.no_grad():
    clip_tokens = clip.tokenize([query]).to(device)
    clip_vector = clip_model.encode_text(clip_tokens).cpu().numpy()[0].tolist()

# === Connect to Qdrant (server)
qdrant = QdrantClient(host="localhost", port=6333)

# === No tag filter by default — search all
filter_condition = None

# === Search function

def search_collection(collection_name, vector, top_k=3):
    try:
        response = qdrant.query_points(
            collection_name=collection_name,
            query=vector,
            limit=top_k,
            with_payload=True,
            query_filter=filter_condition
        )
        results = []
        for r in response.points:
            text = r.payload.get("chunk") or r.payload.get("summary")
            if text:
                results.append({
                    "score": r.score,
                    "text": text,
                    "collection": collection_name,
                    "filename": r.payload.get("filename", "Unknown"),
                    "tag": r.payload.get("tag", "N/A")
                })
        return results
    except Exception as e:
        print(f"⚠️ Error querying {collection_name}: {e}")
        return []

# === Search both collections with the correct vector
print("\n🔎 Searching text memory...")
doc_results_local = search_collection("local_memory", text_vector, top_k=3)

print("\n🔎 Searching image memory...")
img_results = search_collection("image_summary_memory", clip_vector, top_k=3)

# === Combine and sort
combined = sorted(doc_results_local + img_results, key=lambda x: x["score"], reverse=True)

# === Apply threshold and limit to top 1
threshold = 0.50
top_result = combined[0] if combined and combined[0]["score"] >= threshold else None

# === Output
print("\n📚 Top Match:")
if top_result:
    confidence = round(top_result["score"] * 100, 2)
    print(f"💡 Match confidence: {confidence}%")
    print(f"[1] ({top_result['collection']}) [{top_result['tag']}] {top_result['filename']}")
    print(f"🧠 Chunk: {top_result['text']}\n")

    print("----- SYSTEM PROMPT START -----")
    print(f"You have the following memory context (confidence {confidence}%):\n\n{top_result['text']}")
    print("----- SYSTEM PROMPT END -----")
else:
    print("⚠️ No results above confidence threshold.")
