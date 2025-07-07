from pathlib import Path
from config_loader import load_config, get_pdfs
from src.parser import extract_text_blocks, extract_tables, extract_images_and_ocr

# Main function
def main():
    config = load_config(config_file=Path.cwd() / "config.yaml")
    pdf_files = get_pdfs(config)

    all_chunks = []

    for pdf_file in pdf_files:
        # Extract text, tables, and OCR content
        text_chunks = extract_text_blocks(pdf_file)
        table_chunks = extract_tables(pdf_file)
        ocr_chunks = extract_images_and_ocr(pdf_file)

        # Combine everything into one list
        all_chunks.extend(text_chunks + table_chunks + ocr_chunks)

    print(f"\n✅ Total Chunks Extracted: {len(all_chunks)}\n")

    # Print summary of each chunk
    # for chunk in all_chunks:
    #     print(f"[{chunk['type'].upper()}] PDF: {chunk['pdf']} | Page: {chunk['page']} | ID: {chunk['chunk_id']}")
    #     print("-" * 50)


if __name__ == "__main__":
    main()
