import re
from qdrant_client import QdrantClient, models
from sentence_transformers import SentenceTransformer

# === Config
MODEL_NAME = 'BAAI/bge-large-en-v1.5'
TOP_K = 10
SCORE_THRESHOLD = 0.4

# === Load model
model = SentenceTransformer(MODEL_NAME)
print(f"✅ Loaded embedding model: {MODEL_NAME}")

# === Connect to Qdrant
qdrant = QdrantClient(host="localhost", port=6333)

# === Input user question
question = input("🧠 Enter your assistant question: ").strip()
query_vector = model.encode(question).tolist()

# === Search function
def search_memory(collection, vector, top_k=TOP_K):
    try:
        response = qdrant.query_points(
            collection_name=collection,
            query=vector,
            limit=top_k,
            with_payload=True
        )
        results = []
        for point in response.points:
            score = point.score
            if score >= SCORE_THRESHOLD:
                payload = point.payload
                text = payload.get('chunk') or payload.get('summary')
                if text:
                    results.append({
                        'score': score,
                        'text': text.strip(),
                        'filename': payload.get('filename', 'Unknown'),
                        'tag': payload.get('tag', 'N/A'),
                        'collection': collection
                    })
        return results
    except Exception as e:
        print(f"⚠️ Failed to query {collection}: {e}")
        return []

# === Fallback: keyword search for named entities
def keyword_matches(name, collection):
    try:
        response = qdrant.scroll(
            collection_name=collection,
            scroll_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="chunk",
                        match=models.MatchText(text=name)
                    )
                ]
            ),
            limit=TOP_K,
            with_payload=True
        )
        results = []
        for point in response[0]:
            payload = point.payload
            text = payload.get('chunk') or payload.get('summary')
            if text:
                results.append({
                    'score': 0.5,  # Neutral fallback score
                    'text': text.strip(),
                    'filename': payload.get('filename', 'Unknown'),
                    'tag': payload.get('tag', 'N/A'),
                    'collection': collection
                })
        return results
    except Exception as e:
        print(f"⚠️ Keyword fallback failed for {name}: {e}")
        return []

# === Perform searches
text_mem = search_memory("local_memory", query_vector)
img_mem = search_memory("image_summary_memory", query_vector)

# === Fallback search for keywords
fallback_names = []
for word in question.split():
    if word.lower() in ["patrik", "leslie", "john", "kelly"]:
        fallback_names.append(word)

fallback_mem = []
for name in fallback_names:
    fallback_mem += keyword_matches(name, "local_memory")

# === Combine and deduplicate
all_results = text_mem + img_mem + fallback_mem
seen = set()
combined = []
for item in all_results:
    key = (item['filename'], item['text'])
    if key not in seen:
        combined.append(item)
        seen.add(key)

# === Format context block
if not combined:
    print("⚠️ No relevant memory found.")
else:
    print("\n===== MEMORY CONTEXT START =====")
    for item in combined:
        score_pct = round(item['score'] * 100, 2)
        print(f"• From {item['filename']} | Tag: {item['tag']} | Score: {score_pct}%")
        print(item['text'])
        print("")
    print("===== MEMORY CONTEXT END =====")
    print(f"\nUser Question:\n{question}")
