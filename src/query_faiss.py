from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import json

# Load index
index = faiss.read_index("faiss.index")

# Load metadata
with open("chunks_metadata.json", "r") as f:
    chunks = json.load(f)

# Load embedding model
embed_model = SentenceTransformer("all-MiniLM-L6-v2")

# Get query
query = input("Ask your question: ")

# Embed query
query_vector = embed_model.encode([query]).astype('float32')

# Search
D, I = index.search(query_vector, k=3)

print("\n🔍 Top matches:")
for rank, idx in enumerate(I[0]):
    chunk = chunks[idx]
    snippet = str(chunk['content'])[:200]
    print(f"\nRank {rank+1} | Type: {chunk['type']} | Page: {chunk['page']}")
    print(f"{snippet}...")
