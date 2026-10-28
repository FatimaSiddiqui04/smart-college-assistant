"""
Document Loader and Text Preprocessing Module
Extracts text page-by-page from PDF and DOCX files with metadata tracking (source, page, timestamp).
Provides overlapping recursive text chunking as specified in the project report.
"""

import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Union
import io
from pypdf import PdfReader
import docx

import rag_config as config

def clean_extracted_text(text: str) -> str:
    """
    Cleans extracted text by standardizing whitespace, removing excessive blank lines,
    and stripping stray control characters.
    """
    if not text:
        return ""
    # Replace non-breaking spaces and tabs
    text = text.replace('\xa0', ' ').replace('\t', ' ')
    # Normalize multiple newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    # Normalize multiple spaces
    text = re.sub(r' {2,}', ' ', text)
    return text.strip()

def chunk_text(text: str, size: int = config.DEFAULT_CHUNK_SIZE, overlap: int = config.DEFAULT_CHUNK_OVERLAP) -> List[str]:
    """
    Splits text into overlapping chunks of characters.
    Direct implementation matching sample code from Project Report Page 25.
    """
    chunks = []
    start = 0
    text_len = len(text)
    
    if text_len == 0:
        return chunks
        
    while start < text_len:
        end = start + size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= text_len:
            break
        start += size - overlap
    return chunks

def load_pdf(source: Union[str, Path, io.BytesIO], filename: str) -> List[Dict[str, Any]]:
    """
    Reads a PDF file page by page and returns list of page dictionaries:
    [{'text': str, 'page': int, 'source': str}]
    """
    pages_data = []
    reader = PdfReader(source)
    for page_idx, page in enumerate(reader.pages, start=1):
        raw_text = page.extract_text() or ""
        cleaned = clean_extracted_text(raw_text)
        if cleaned:
            pages_data.append({
                "text": cleaned,
                "page": page_idx,
                "source": filename
            })
    return pages_data

def load_docx(source: Union[str, Path, io.BytesIO], filename: str) -> List[Dict[str, Any]]:
    """
    Reads a Microsoft Word DOCX file and returns structured paragraph blocks.
    Groups approximately every 500 words or section breaks as a 'page' to maintain citations.
    """
    doc = docx.Document(source)
    pages_data = []
    current_page_text = []
    current_page_num = 1
    current_word_count = 0
    
    for p in doc.paragraphs:
        p_text = clean_extracted_text(p.text)
        if not p_text:
            continue
        words = p_text.split()
        current_word_count += len(words)
        current_page_text.append(p_text)
        
        # Approximate ~300 words per page for DOCX
        if current_word_count >= 300:
            full_page_text = "\n\n".join(current_page_text)
            pages_data.append({
                "text": full_page_text,
                "page": current_page_num,
                "source": filename
            })
            current_page_text = []
            current_page_num += 1
            current_word_count = 0

    if current_page_text:
        pages_data.append({
            "text": "\n\n".join(current_page_text),
            "page": current_page_num,
            "source": filename
        })
        
    return pages_data

def process_file_to_chunks(source: Union[str, Path, io.BytesIO], filename: str, 
                           chunk_size: int = config.DEFAULT_CHUNK_SIZE, 
                           chunk_overlap: int = config.DEFAULT_CHUNK_OVERLAP) -> List[Dict[str, Any]]:
    """
    Parses a document (PDF or DOCX), breaks each page into overlapping chunks,
    and returns a list of chunk metadata dictionaries ready for vector database storage.
    """
    ext = Path(filename).suffix.lower()
    if ext == ".pdf":
        pages = load_pdf(source, filename)
    elif ext in [".docx", ".doc"]:
        pages = load_docx(source, filename)
    else:
        # Generic text file support
        if isinstance(source, (str, Path)):
            with open(source, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        else:
            content = source.read().decode("utf-8", errors="ignore")
        pages = [{"text": clean_extracted_text(content), "page": 1, "source": filename}]

    all_chunks = []
    upload_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for page_info in pages:
        page_no = page_info["page"]
        raw_chunks = chunk_text(page_info["text"], size=chunk_size, overlap=chunk_overlap)
        for chunk_idx, c_text in enumerate(raw_chunks):
            # Clean safe ID matching sample code: f"{name}-{page_no}-{chunk_idx}"
            safe_name = re.sub(r'[^a-zA-Z0-9_\-.]', '_', filename)
            chunk_id = f"{safe_name}-{page_no}-{chunk_idx}"
            all_chunks.append({
                "id": chunk_id,
                "document": c_text,
                "source": filename,
                "page": page_no,
                "chunk_index": chunk_idx,
                "upload_date": upload_date
            })

    return all_chunks
