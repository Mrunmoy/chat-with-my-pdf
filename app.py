import streamlit as st
import faiss
from sentence_transformers import SentenceTransformer
from ollama import Client
import json

# === Load FAISS index + metadata ===
faiss_index = faiss.read_index("faiss.index")

with open("chunks_metadata.json", "r") as f:
    chunks = json.load(f)

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# === Connect to local Ollama ===
ollama_client = Client(host="http://localhost:11434")

# === Streamlit page setup ===
st.set_page_config(page_title="Chat with My PDFs", page_icon="📚")
st.title("📚 Chat with My PDFs")

# === Initialize chat history ===
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

# === User input ===
question = st.text_input("Ask a question:", key="user_question")

if question.strip() != "":
    # === Show spinner while thinking ===
    with st.spinner("🤔 Hang on, figuring it out..."):
        # Embed query
        query_embedding = embedding_model.encode([question])
        distances, indices = faiss_index.search(query_embedding, k=3)

        # Get top chunks
        retrieved_chunks = []
        for i in indices[0]:
            retrieved_chunks.append(chunks[i]['content'])

        # Build prompt
        context = "\n".join(f"- {c}" for c in retrieved_chunks)
        prompt = f"""
Use ONLY the context below to answer the question.
If the answer is not in the context, say you don't know.

Context:
{context}

Question: {question}

Answer:
"""

        # Call Ollama locally
        response = ollama_client.chat(
            model="mistral",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )

    final_answer = response['message']['content']

    # === Show final answer ===
    st.subheader("Answer")
    st.write(final_answer)

    # === Show what it's thinking with ===
    with st.expander("👀 What I’m looking at..."):
        st.markdown("**Prompt to LLM:**")
        st.code(prompt)

        st.markdown("**Context chunks:**")
        for i, chunk in enumerate(retrieved_chunks):
            if isinstance(chunk, list):
                chunk_text = "\n".join(str(row) for row in chunk)
            else:
                chunk_text = str(chunk)
            st.markdown(f"**Chunk {i+1}**")
            st.write(chunk_text[:300] + "...")


    # === Show source chunks nicely ===
    with st.expander("Source Chunks"):
        for i, chunk in enumerate(retrieved_chunks):
            if isinstance(chunk, list):
                chunk_text = "\n".join(str(row) for row in chunk)
            else:
                chunk_text = str(chunk)

            st.markdown(f"**Chunk {i+1}**")
            st.write(chunk_text[:300] + "...")

    # === Save Q&A to chat history ===
    st.session_state['chat_history'].append({
        'question': question,
        'answer': final_answer
    })

# === Sidebar: show chat history ===
with st.sidebar:
    st.header("💬 Chat History")
    for chat in st.session_state['chat_history']:
        st.markdown(f"**Q:** {chat['question']}")
        st.markdown(f"**A:** {chat['answer']}")
        st.markdown("---")
