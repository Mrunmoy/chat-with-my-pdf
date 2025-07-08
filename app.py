import streamlit as st
import faiss
from sentence_transformers import SentenceTransformer
from ollama import Client
import json
import os

# === Load embedding model + Ollama once ===
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
ollama_client = Client(host="http://localhost:11434")

# === Streamlit page ===
st.set_page_config(page_title="Chat with My PDFs", page_icon="📚")
st.title("Chat with My PDFs")

# === Multi-PDF upload ===
uploaded_files = st.file_uploader(
    "Upload one or more PDFs to add to the database",
    type=["pdf"],
    accept_multiple_files=True
)

if uploaded_files:
    with st.spinner("🔄 Parsing, chunking, and embedding uploaded PDFs..."):
        all_chunks = []

        for uploaded_file in uploaded_files:
            # Save to pdfs/ folder
            pdf_path = f"pdfs/{uploaded_file.name}"
            with open(pdf_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.info(f"Saved: {uploaded_file.name}")

            # Call your existing parser
            from src.parser import extract_text_blocks, extract_tables, extract_images_and_ocr

            text_chunks = extract_text_blocks(pdf_path)
            table_chunks = extract_tables(pdf_path)
            ocr_chunks = extract_images_and_ocr(pdf_path)

            all_chunks.extend(text_chunks + table_chunks + ocr_chunks)

        if all_chunks:
            # Filter out empty or junk chunks
            clean_chunks = [
                c for c in all_chunks
                if (
                    c.get("content")
                    and (
                        (isinstance(c["content"], str) and c["content"].strip() != "")
                        or (isinstance(c["content"], list) and len(c["content"]) > 0)
                    )
                )
            ]

            # Prepare texts for embedding
            texts = [
                c["content"] if isinstance(c["content"], str)
                else "\n".join(str(row) for row in c["content"])
                for c in clean_chunks
            ]

            # Embed
            embeddings = embedding_model.encode(texts)

            # Rebuild FAISS index
            dim = embeddings.shape[1]
            faiss_index = faiss.IndexFlatL2(dim)
            faiss_index.add(embeddings)

            faiss.write_index(faiss_index, "faiss.index")

            # Save only clean chunks
            with open("chunks_metadata.json", "w") as f:
                json.dump(clean_chunks, f)

            st.success("All PDFs processed! Vector DB updated.")
        else:
            st.warning("No chunks extracted. Check your PDFs!")

# === Load or reload index & metadata ===
if os.path.exists("faiss.index") and os.path.exists("chunks_metadata.json"):
    faiss_index = faiss.read_index("faiss.index")
    with open("chunks_metadata.json", "r") as f:
        chunks = json.load(f)
else:
    st.error("No index found. Please upload PDFs first!")
    st.stop()

# === Initialize chat history ===
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

# === User input ===
question = st.text_input("Ask a question:", key="user_question")

if question.strip() != "":
    with st.spinner("🤔 Hang on, figuring it out..."):
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

    with st.expander("👀 What I’m looking at..."):
        st.markdown("**Context chunks:**")
        for i, chunk in enumerate(retrieved_chunks):
            if isinstance(chunk, list):
                flat_lines = []
                for row in chunk:
                    if isinstance(row, list):
                        flat_lines.append(" | ".join(str(cell) for cell in row))
                    else:
                        flat_lines.append(str(row))
                chunk_text = "\n".join(flat_lines)
            else:
                chunk_text = str(chunk)

            st.markdown(f"**Chunk {i+1}**")
            st.write(chunk_text[:300] + "...")

    with st.expander("Source Chunks"):
        for i, chunk in enumerate(retrieved_chunks):
            if isinstance(chunk, list):
                # Flatten any sub-lists safely
                flat_lines = []
                for row in chunk:
                    if isinstance(row, list):
                        flat_lines.append(" | ".join(str(cell) for cell in row))
                    else:
                        flat_lines.append(str(row))
                chunk_text = "\n".join(flat_lines)
            else:
                chunk_text = str(chunk)

            st.markdown(f"**Chunk {i+1}**")
            st.write(chunk_text[:300] + "...")

    st.session_state['chat_history'].append({
        'question': question,
        'answer': final_answer
    })

# === Sidebar chat history ===
with st.sidebar:
    st.header("💬 Chat History")
    for chat in st.session_state['chat_history']:
        st.markdown(f"**Q:** {chat['question']}")
        st.markdown(f"**A:** {chat['answer']}")
        st.markdown("---")
