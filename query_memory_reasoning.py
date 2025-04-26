import os
import re
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
query = input("🔍 Enter your memory question: ").strip()

# === Encode query
text_vector = text_model.encode("query: " + query).tolist()
with torch.no_grad():
    clip_tokens = clip.tokenize([query]).to(device)
    clip_vector = clip_model.encode_text(clip_tokens).cpu().numpy()[0].tolist()

# === Extract target keyword for entity match
name_match = None
for word in query.split():
    if word.lower() in ["john", "kelly", "leslie"]:
        name_match = word.lower()
        break

# === Connect to Qdrant
qdrant = QdrantClient(host="localhost", port=6333)

# === Search function
def search_collection(collection_name, vector, top_k=5):
    try:
        response = qdrant.query_points(
            collection_name=collection_name,
            query=vector,
            limit=top_k,
            with_payload=True
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

# === Perform searches
doc_results = search_collection("local_memory", text_vector)
img_results = search_collection("image_summary_memory", clip_vector)

combined = sorted(doc_results + img_results, key=lambda x: x["score"], reverse=True)

# === Reasoning Filter
relevant_results = []
for res in combined:
    if name_match:
        if re.search(rf"\b{name_match}\b", res['text'], re.IGNORECASE):
            relevant_results.append(res)
    else:
        relevant_results.append(res)

# === Final Output
print("\n📚 Best Match (After Reasoning):")
if relevant_results:
    top = relevant_results[0]
    confidence = round(top['score'] * 100, 2)
    print(f"💡 Match confidence: {confidence}%")
    print(f"[1] ({top['collection']}) [{top['tag']}] {top['filename']}")
    print(f"🧠 Chunk: {top['text']}")
    print("\n----- SYSTEM PROMPT START -----")
    print(f"You have the following memory context (confidence {confidence}%):\n\n{top['text']}")
    print("----- SYSTEM PROMPT END -----")
else:
    print("⚠️ No matching information found for this question.")
    if name_match:
        print(f"ℹ️ Memory does not contain any reference to '{name_match}'.")