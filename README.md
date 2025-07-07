# Chat With My PDF (Local, Private, Free)

Implements a privacy-focused, fully local PDF semantic search pipeline
## What this project does

- Implements a privacy-focused, fully local PDF semantic search pipeline
- Processes your PDF documents by:
  - Extracting plain text
  - Extracting tables
  - Performing OCR on images when needed
- Divides the extracted content into manageable chunks
- Embeds each chunk using a lightweight, locally-run sentence transformer model
- Stores embeddings in a FAISS vector database for fast similarity search
- Lets you ask questions in natural language and returns the most semantically relevant chunks
- Runs entirely offline — no external APIs — keeping your data private
- Current version returns the top 3 closest matches to your query
- Great for basic semantic search, but not comparable to a full ChatGPT-like system
- Perfect for users who prioritize privacy and want a simple, local solution for semantic PDF search without cloud dependencies

## Example: What a chunk looks like

Here’s a single chunk in JSON format:

```json
{
  "pdf": "pdfs/ATOMS-AND-MOLECULES.pdf",
  "page": 5,
  "chunk_id": "text_0",
  "type": "text",
  "content": "Dalton's Atomic Theory states that all matter is made up of indivisible atoms..."
}
```

**What each field means:**

- **`pdf`**: the path to the original PDF file  
- **`page`**: page number (1-based) in the PDF  
- **`chunk_id`**: unique ID for this chunk within that page/type  
- **`type`**: whether this chunk is `text`, `table`, or `ocr`  
- **`content`**: the actual text, table rows, or OCR result

Each chunk is embedded into the vector store for semantic search.  
When you query, you get back the top chunks with their source info — so you can trace results back to the exact page in your PDF.

---

## Project structure

```
chat-with-my-pdf/
├── config.yaml              # YAML config: list your PDFs, embedding model, vector DB
├── config_loader.py         # Loads your config and exposes helper functions
├── main.py                  # Parses PDF(s) into chunks and saves them locally
├── src/
│   ├── __init__.py
│   ├── parser.py            # Extracts text, tables, and OCR from PDFs
│   ├── embed_faiss.py       # Embeds chunks & creates FAISS index
│   ├── query_faiss.py       # Example CLI to ask questions over your vector DB
├── pdfs/                    # Put your local PDFs here (not committed)
├── .gitignore               # Keeps private data local
└── requirements.txt
```

---

## How to use it

### 1️⃣ Clone & set up your environment

```bash
git clone https://github.com/Mrunmoy/chat-with-my-pdf.git
cd chat-with-my-pdf

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

### 2️⃣ Add your PDF(s)

- Put your PDF(s) in the `pdfs/` folder.
- List them in `config.yaml`:
  ```yaml
  pdfs:
    - pdfs/your-book.pdf
  embedding_model: all-MiniLM-L6-v2
  vector_db: faiss
  ```

---

### 3️⃣ Parse the PDF(s)

```bash
python3 main.py
```

This extracts chunks and (optionally) saves them to `parsed_chunks.json`.

---

### 4️⃣ Embed chunks & create vector index

```bash
python3 -m src.embed_faiss
```

This generates:
- `faiss.index` — your local semantic search index  
- `chunks_metadata.json` — metadata for mapping back to pages

> ⚠️ **Note:** These files contain private text from your PDF. They are **.gitignored**  
> so they won’t be committed.

---

### 5️⃣ Search your PDF with natural language

```bash
python3 -m src.query_faiss
```

Type any question — get back the top matching chunks!

---

## Example: How it works in practice

Below is an example of running the `query_faiss.py` script to search for *Dalton's Atomic Theory* in a local PDF:

```bash
$ python3 -m src.query_faiss
Ask your question: Dalton's Atomic Theory

Top matches:

Rank 1 | Type: text | Page: 3
ATOMS AND MOLECULES
33
We might think that if atoms are so
insignificant in size, why should we care about
them? This is because our entire world is
made up of atoms. We may not be able to see
them, b...

Rank 2 | Type: text | Page: 6
SCIENCE
36
3.3.1 MOLECULES OF ELEMENTS
The molecules of an element are constituted
by the same type of atoms. Molecules of many
elements, such as argon (Ar), helium (He) etc.
are made up of only one a...

Rank 3 | Type: text | Page: 5
ATOMS AND MOLECULES
35
whole numbers or as near to a whole numbers
as possible. While searching for various
atomic mass units, scientists initially took 1/
16 of the mass of an atom of naturally
occur...
```

This shows how your query returns the most semantically relevant chunks with page numbers,
so you can trace answers back to the source PDF.

---

## Why this is private

- You keep your PDFs and parsed text **local only**.
- You run your embeddings offline.
- Your `.gitignore` ensures you never push your `faiss.index` or chunk metadata.

---

## Built with

- [PyMuPDF](https://pymupdf.readthedocs.io/) for PDF text extraction
- [pdfplumber](https://github.com/jsvine/pdfplumber) for table extraction
- [pytesseract](https://github.com/madmaze/pytesseract) for OCR
- [sentence-transformers](https://www.sbert.net/) for local embeddings
- [FAISS](https://github.com/facebookresearch/faiss) for fast local vector search

---

## License

MIT

Personal use only — this repo is for **educational and research purposes**.  
Please respect any copyright for the PDFs you process!

---

