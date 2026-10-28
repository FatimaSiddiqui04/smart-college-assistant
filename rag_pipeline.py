"""
Smart College Assistant RAG Pipeline
Orchestrates document indexing, ChromaDB persistent storage, semantic vector retrieval with cosine threshold,
and context-grounded response generation.
Direct implementation of Chapter 4 & Chapter 6 from the project report.
"""

import os
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
import chromadb
from chromadb.config import Settings

import rag_config as config
from document_loader import process_file_to_chunks
from embeddings import embed_texts, embed_query

class CollegeRAGPipeline:
    def __init__(self, persist_dir: str = config.CHROMA_STORE_DIR, collection_name: str = config.CHROMA_COLLECTION_NAME):
        self.persist_dir = persist_dir
        self.collection_name = collection_name
        
        # Initialize persistent ChromaDB client
        self.client = chromadb.PersistentClient(path=self.persist_dir)
        
        # Get or create collection with cosine similarity metric (hnsw:space = cosine)
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": config.DISTANCE_METRIC}
        )

    def index_document(self, file_path_or_bytes, filename: str,
                       chunk_size: int = config.DEFAULT_CHUNK_SIZE,
                       chunk_overlap: int = config.DEFAULT_CHUNK_OVERLAP) -> int:
        """
        Indexes a single document (PDF or DOCX) into ChromaDB.
        Replaces any existing chunks for the same filename to avoid stale duplicates.
        """
        # Remove previous chunks of the same document if any exist
        self.delete_document(filename)
        
        chunks = process_file_to_chunks(
            source=file_path_or_bytes,
            filename=filename,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        
        if not chunks:
            return 0
            
        ids = [c["id"] for c in chunks]
        documents = [c["document"] for c in chunks]
        metadatas = [{
            "source": c["source"],
            "page": int(c["page"]),
            "chunk_index": int(c["chunk_index"]),
            "upload_date": c["upload_date"]
        } for c in chunks]
        
        # Compute embeddings via all-MiniLM-L6-v2
        embeddings = embed_texts(documents)
        
        # Store in ChromaDB
        self.collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings
        )
        return len(chunks)

    def retrieve(self, question: str, k: int = config.DEFAULT_TOP_K,
                 threshold: float = config.DEFAULT_SCORE_THRESHOLD) -> List[Dict[str, Any]]:
        """
        Retrieves top-k relevant chunks whose cosine similarity meets the threshold.
        Exact logic matching sample code from Project Report Page 26/29:
        if 1 - dist >= threshold: hits.append((doc, meta))
        """
        total_items = self.collection.count()
        if total_items == 0:
            return []

        # Ensure k does not exceed number of stored chunks
        effective_k = min(k, total_items)
        if effective_k <= 0:
            return []

        q_vec = embed_query(question)
        res = self.collection.query(
            query_embeddings=[q_vec],
            n_results=effective_k
        )
        
        hits = []
        docs = res.get("documents", [[]])[0]
        metas = res.get("metadatas", [[]])[0]
        dists = res.get("distances", [[]])[0]
        
        for doc, meta, dist in zip(docs, metas, dists):
            # In Chroma cosine space: distance = 1 - cosine_similarity
            # Therefore: similarity = 1 - distance
            similarity = 1.0 - float(dist)
            if similarity >= threshold:
                hits.append({
                    "text": doc,
                    "metadata": meta,
                    "similarity": round(similarity, 4),
                    "source": meta.get("source", "Unknown"),
                    "page": meta.get("page", 1)
                })
                
        # Sort descending by similarity
        hits.sort(key=lambda x: x["similarity"], reverse=True)
        return hits

    def get_indexed_documents(self) -> List[Dict[str, Any]]:
        """
        Returns a summary list of all unique documents currently indexed in ChromaDB.
        """
        total_count = self.collection.count()
        if total_count == 0:
            return []
            
        data = self.collection.get(include=["metadatas"])
        metadatas = data.get("metadatas", [])
        
        doc_stats = {}
        for m in metadatas:
            if not m:
                continue
            src = m.get("source", "Unknown")
            page = m.get("page", 1)
            date = m.get("upload_date", "-")
            
            if src not in doc_stats:
                doc_stats[src] = {
                    "source": src,
                    "chunk_count": 0,
                    "pages": set(),
                    "upload_date": date
                }
            doc_stats[src]["chunk_count"] += 1
            doc_stats[src]["pages"].add(page)
            
        summary = []
        for src, info in doc_stats.items():
            summary.append({
                "source": src,
                "chunks": info["chunk_count"],
                "total_pages": len(info["pages"]),
                "upload_date": info["upload_date"]
            })
        return sorted(summary, key=lambda x: x["source"])

    def delete_document(self, filename: str) -> int:
        """
        Deletes all chunks belonging to a specific document.
        """
        try:
            # Query IDs with this source
            res = self.collection.get(where={"source": filename})
            ids_to_del = res.get("ids", [])
            if ids_to_del:
                self.collection.delete(ids=ids_to_del)
                return len(ids_to_del)
        except Exception as e:
            print(f"Notice: could not delete {filename}: {e}")
        return 0

    def reset_index(self):
        """
        Clears the entire ChromaDB collection.
        """
        try:
            self.client.delete_collection(self.collection_name)
        except Exception:
            pass
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": config.DISTANCE_METRIC}
        )

    def index_all_sample_documents(self) -> Dict[str, int]:
        """
        Finds and indexes all sample PDF files in the sample_documents directory.
        """
        sample_dir = Path(config.SAMPLE_DOCS_DIR)
        results = {}
        if not sample_dir.exists():
            return results
            
        for file_path in sample_dir.glob("*.pdf"):
            count = self.index_document(str(file_path), file_path.name)
            results[file_path.name] = count
        return results

    def build_prompt_context(self, hits: List[Dict[str, Any]]) -> str:
        """
        Constructs context string with source citations for the LLM.
        """
        context_parts = []
        for i, hit in enumerate(hits, start=1):
            source = hit["source"]
            page = hit["page"]
            text = hit["text"]
            context_parts.append(f"[Document: {source}, Page {page}]\n{text}")
        return "\n\n".join(context_parts)
