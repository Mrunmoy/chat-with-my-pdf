import faiss
from sentence_transformers import SentenceTransformer
from ollama import Client
import pickle
import json

# === Load your saved FAISS index ===
faiss_index = faiss.read_index("faiss.index")

# Load your chunk metadata (JSON or pickle)
with open("chunks_metadata.json", "rb") as f:
    chunks = json.load(f)# pickle.load(f)

# Load your embedding model (same one you used to build the index)
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# === Connect to Ollama ===
ollama_client = Client(host="http://localhost:11434")

print("\nLocal RAG chat is ready!")

while True:
    question = input("\nYour question (or 'exit'): ")
    if question.lower() == "exit":
        break

    # Embed the question
    query_embedding = embedding_model.encode([question])

    # Search FAISS for top N
    distances, indices = faiss_index.search(query_embedding, k=3)

    retrieved_chunks = []
    for i in indices[0]:
        retrieved_chunks.append(chunks[i]['content'])

    # Build the prompt
    context = "\n".join(f"- {c}" for c in retrieved_chunks)
    prompt = f"""
Use ONLY the context below to answer the question.
If the answer is not in the context, say you don't know.

Context:
{context}

Question: {question}

Answer:
"""

    # Call your local LLM
    response = ollama_client.chat(
        model="mistral",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )

    print("\nAnswer:")
    print(response['message']['content'])

    # Optional: show source chunks
    print("\nSource Chunks:")
    for chunk in retrieved_chunks:
        print(f"- {chunk[:100]}...")  # Preview only
