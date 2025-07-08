import streamlit as st
import faiss
from sentence_transformers import SentenceTransformer
from ollama import Client
import json

# === Load once ===
faiss_index = faiss.read_index("faiss.index")

with open("chunks_metadata.json", "r") as f:
    chunks = json.load(f)

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

ollama_client = Client(host="http://localhost:11434")

st.set_page_config(page_title="Chat with My PDFs", page_icon="📚")
st.title("Chat with My PDFs")

# === Widget with unique key ===
question = st.text_input("Ask a question:", key="user_question")

# === Only do the heavy lifting if there's input ===
if question.strip() != "":
    query_embedding = embedding_model.encode([question])
    distances, indices = faiss_index.search(query_embedding, k=3)

    retrieved_chunks = []
    for i in indices[0]:
        retrieved_chunks.append(chunks[i]['content'])

    context = "\n".join(f"- {c}" for c in retrieved_chunks)
    prompt = f"""
Use ONLY the context below to answer the question.
If the answer is not in the context, say you don't know.

Context:
{context}

Question: {question}

Answer:
"""

    response = ollama_client.chat(
        model="mistral",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )

    final_answer = response['message']['content']

    st.subheader("Answer")
    st.write(final_answer)

    with st.expander("📚 Source Chunks"):
        for i, chunk in enumerate(retrieved_chunks):
            if isinstance(chunk, list):
                chunk_text = "\n".join(str(row) for row in chunk)
            else:
                chunk_text = str(chunk)
            
            st.markdown(f"**Chunk {i+1}**")
            st.write(chunk_text[:300] + "...")


