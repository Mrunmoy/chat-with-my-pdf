import fitz  # PyMuPDF, for reading PDFs and extracting text & images
import pdfplumber  # For extracting tables from PDFs
import pytesseract  # Python wrapper for Tesseract OCR
from PIL import Image  # Python Imaging Library for image processing
import io  # For handling image bytes


# -------------------------------------------
# Chunk structure for all extracted elements:
#
# {
#   "pdf": "path/to/file.pdf",     # Full path to the PDF this chunk came from
#   "page": 5,                     # Page number (1-based)
#   "chunk_id": "text_0",          # Unique ID for this chunk on that page
#   "type": "text" | "table" | "ocr",  # Type of content
#   "content": "..." or [[...]],   # The actual content:
#                                  #  - text: paragraph string
#                                  #  - table: nested list (rows & cells)
#                                  #  - ocr: text extracted from an image
# }
#
# This structure ensures each piece is:
# - Traceable to its PDF source
# - Easy to embed later
# - Useful for semantic search & retrieval
# -------------------------------------------


# ------------------------
# Function: extract_text_blocks
# ------------------------
# This function reads all text content from a PDF file.
# It splits text into paragraphs (separated by double newlines) for easier chunking.
# Each paragraph becomes a "chunk" that we can embed later.
def extract_text_blocks(pdf_path):
    doc = fitz.open(pdf_path)
    all_chunks = []

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        # Extract plain text for this page
        text = page.get_text("text")

        # Split by double newlines into paragraphs, strip whitespace
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]

        for i, para in enumerate(paragraphs):
            # Add each paragraph as its own chunk with metadata
            all_chunks.append({
                "pdf": pdf_path,
                "page": page_num + 1,
                "chunk_id": f"text_{i}",
                "type": "text",
                "content": para
            })

    return all_chunks


# ------------------------
# Function: extract_tables
# ------------------------
# This function uses pdfplumber to find tables in the PDF.
# Each table is added as its own chunk, preserving rows & columns.
def extract_tables(pdf_path):
    all_tables = []
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            tables = page.extract_tables()
            for i, table in enumerate(tables):
                all_tables.append({
                    "pdf": pdf_path,
                    "page": page_num + 1,
                    "chunk_id": f"table_{i}",
                    "type": "table",
                    "content": table  # Table is a list of rows
                })
    return all_tables


# ------------------------
# Function: extract_images_and_ocr
# ------------------------
# This function looks for images on each page.
# If an image exists, we run it through Tesseract OCR to extract any text.
# Useful for scanned PDFs or pages with text-as-image.
def extract_images_and_ocr(pdf_path):
    doc = fitz.open(pdf_path)
    ocr_chunks = []

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        images = page.get_images(full=True)

        for img_index, img in enumerate(images):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]

            # Load image as RGB for Tesseract
            img_pil = Image.open(io.BytesIO(image_bytes)).convert("RGB")

            # Run OCR
            ocr_text = pytesseract.image_to_string(img_pil)

            if ocr_text.strip():
                ocr_chunks.append({
                    "pdf": pdf_path,
                    "page": page_num + 1,
                    "chunk_id": f"ocr_{img_index}",
                    "type": "ocr",
                    "content": ocr_text.strip()
                })

    return ocr_chunks
