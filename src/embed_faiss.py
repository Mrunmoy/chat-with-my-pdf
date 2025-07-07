"""
This script:
1. Loads your config.yaml to get PDF files and embedding model.
2. Parses the PDFs to get text, tables, and OCR chunks (or later: loads pre-chunked data).
3. Uses a local embedding model (SentenceTransformers) to create embeddings for each chunk.
4. Indexes the embeddings in a FAISS vector store.
5. Runs a simple semantic search query to test everything works.
"""

from sentence_transformers import SentenceTransformer
import faiss
import json
import numpy as np

# Import your config loader and parser
from config_loader import load_config, get_pdfs
from src.parser import extract_text_blocks, extract_tables, extract_images_and_ocr

# -------------------------------
# Step 1: Load config
# -------------------------------
config = load_config()

# Get list of PDF files
pdf_files = get_pdfs(config)

# Get the embedding model name (from config.yaml)
embedding_model_name = config.get("embedding_model", "all-MiniLM-L6-v2")

# -------------------------------
# Step 2: Load embedding model
# -------------------------------
print(f"Loading local embedding model: {embedding_model_name}")
embed_model = SentenceTransformer(embedding_model_name)

# -------------------------------
# Step 3: Parse PDFs again
# -------------------------------
# For now, parse PDFs every time.
# Later, you can save chunks to JSON and just load that.
all_chunks = []

for pdf_file in pdf_files:
    text_chunks = extract_text_blocks(pdf_file)
    table_chunks = extract_tables(pdf_file)
    ocr_chunks = extract_images_and_ocr(pdf_file)
    all_chunks.extend(text_chunks + table_chunks + ocr_chunks)

print(f"Parsed {len(all_chunks)} total chunks from {len(pdf_files)} PDF(s).")

# -------------------------------
# Step 4: Prepare text data
# -------------------------------
# Make sure each chunk is a string. Tables get converted to strings too.
texts = [
    chunk['content'] if isinstance(chunk['content'], str)
    else str(chunk['content'])
    for chunk in all_chunks
]

# -------------------------------
# Step 5: Embed chunks
# -------------------------------
print(f"Embedding all chunks...")
embeddings = embed_model.encode(texts, show_progress_bar=True)
embeddings = np.array(embeddings).astype('float32')  # FAISS needs float32

# -------------------------------
# Step 6: Create FAISS index
# -------------------------------
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)  # L2 distance for similarity
index.add(embeddings)

print(f"FAISS index created. Vector dimension: {dimension}")
print(f"Indexed {len(texts)} chunks.")

# Save FAISS index to file
faiss.write_index(index, "faiss.index")

# Save chunks metadata to file
with open("chunks_metadata.json", "w") as f:
    json.dump(all_chunks, f, indent=2)

print("Saved FAISS index and chunk metadata.")

# -------------------------------
# Step 7: Run test query
# -------------------------------
query = "What is Dalton's Atomic Theory?"
print(f"\nTest query: {query}")

# Embed the query
query_vector = embed_model.encode([query]).astype('float32')

# Search for top-3 nearest chunks
D, I = index.search(query_vector, k=3)

print("\nTop matches:")
for rank, idx in enumerate(I[0]):
    print(f"\nRank {rank+1} | Chunk index: {idx} | Distance: {D[0][rank]:.4f}")
    print(f"Content: {texts[idx][:200]}...")  # Show a snippet
