"""
Configuration settings for Smart College Assistant (RAG-Based)
Mini Project 1A - Atharva College of Engineering / University of Mumbai
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Base Directory
BASE_DIR = Path(__file__).resolve().parent

# Load environment variables (.env file)
load_dotenv(BASE_DIR / ".env")

# Storage Directories
CHROMA_STORE_DIR = str(BASE_DIR / "chroma_store")
UPLOAD_DIR = str(BASE_DIR / "uploaded_documents")
SAMPLE_DOCS_DIR = str(BASE_DIR / "sample_documents")

os.makedirs(CHROMA_STORE_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(SAMPLE_DOCS_DIR, exist_ok=True)

# ChromaDB Settings
CHROMA_COLLECTION_NAME = "college_docs"
DISTANCE_METRIC = "cosine" # Uses cosine similarity: hnsw:space = cosine

# RAG Pipeline Parameters (From Project Report Table 6.2)
DEFAULT_CHUNK_SIZE = 800       # Size of each searchable piece in characters
DEFAULT_CHUNK_OVERLAP = 150    # Keeps context across chunk borders
DEFAULT_TOP_K = 4              # Number of context chunks retrieved for LLM
DEFAULT_SCORE_THRESHOLD = 0.30 # Cosine similarity threshold (rejects irrelevant results)

# Embedding Model Specification
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
EMBEDDING_DIMENSIONS = 384

# LLM Generation Parameters
DEFAULT_LLM_TEMPERATURE = 0.1   # Keeps answers strictly factual (0 - 0.2 recommended)
MAX_RESPONSE_TOKENS = 512

# Standard Negative Response (Specified in Project Report Page 19 & 28)
NOT_FOUND_MESSAGE = "I could not find this in the college documents."

# Prompt Template (Specified in Project Report Page 19)
RAG_SYSTEM_PROMPT = """You are the Smart College Assistant for Atharva College of Engineering.
Answer the question using ONLY the provided context below.
If the answer cannot be found in the context, reply exactly:
"{not_found_message}"

RULES:
1. Do not invent, speculate, or hallucinate facts, dates, rules, or fees not present in the context.
2. Formulate a concise, clear answer.
3. Explicitly cite the source document name and page number at the end of your answer.

Context:
{context}

Question:
{question}
"""
