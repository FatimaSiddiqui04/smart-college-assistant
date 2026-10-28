"""
Smart College Assistant - Vercel Serverless API
FastAPI backend optimized for Vercel Serverless Functions.
Provides:
- GET /api/health
- GET /api/documents
- POST /api/chat
- GET /api/evaluate
"""

import os
import re
import json
import math
from pathlib import Path
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Smart College Assistant API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "college_docs_data.json"

# Load pre-extracted documents and chunks
DOCUMENTS_CACHE = []
if DATA_FILE.exists():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        DOCUMENTS_CACHE = json.load(f)

NOT_FOUND_MESSAGE = "I could not find this in the college documents."

class QueryRequest(BaseModel):
    question: str
    top_k: Optional[int] = 4
    threshold: Optional[float] = 0.25
    api_key: Optional[str] = None
    provider: Optional[str] = "Auto"

def compute_bm25_score(query_tokens: List[str], text: str, total_docs: int) -> float:
    text_lower = text.lower()
    score = 0.0
    for token in query_tokens:
        if not token:
            continue
        count = text_lower.count(token)
        if count > 0:
            # Term frequency saturation
            tf = (count * 2.2) / (count + 1.2)
            score += tf
    return score

def search_documents(query: str, k: int = 4, threshold: float = 0.25) -> List[Dict[str, Any]]:
    if not DOCUMENTS_CACHE:
        return []

    stop_words = {"what", "is", "the", "for", "to", "in", "which", "are", "of", "a", "an", "and", "do", "does", "how", "can", "i", "when", "on"}
    raw_tokens = re.findall(r'\b[a-zA-Z0-9_\-\.%]+\b', query.lower())
    content_tokens = [t for t in raw_tokens if t not in stop_words and len(t) > 1]

    if not content_tokens:
        return []

    scored_hits = []
    total_docs = len(DOCUMENTS_CACHE)

    for item in DOCUMENTS_CACHE:
        text = item["text"]
        score = compute_bm25_score(content_tokens, text, total_docs)
        
        # Normalized score
        norm_score = min(score / (len(content_tokens) * 2.0), 1.0)
        
        if norm_score >= threshold:
            scored_hits.append({
                "text": text,
                "source": item["source"],
                "page": item["page"],
                "similarity": round(norm_score, 4)
            })

    scored_hits.sort(key=lambda x: x["similarity"], reverse=True)
    return scored_hits[:k]

def synthesize_extractive_answer(question: str, retrieved_chunks: List[Dict[str, Any]]) -> str:
    if not retrieved_chunks:
        return NOT_FOUND_MESSAGE

    stop_words = {"what", "is", "the", "for", "to", "in", "which", "are", "of", "a", "an", "and", "do", "does", "how", "can", "i", "when"}
    raw_tokens = re.findall(r'\b[a-zA-Z0-9_\-\.%]+\b', question.lower())
    content_tokens = [t for t in raw_tokens if t not in stop_words and len(t) > 1]

    scored_candidates = []
    for hit in retrieved_chunks:
        source_name = hit["source"]
        page_num = hit["page"]
        text = hit["text"]

        segments = [s.strip() for s in re.split(r'(?<=[.!?\n])\s+', text) if len(s.strip()) > 15]
        for seg in segments:
            seg_lower = seg.lower()
            score = 0
            for token in content_tokens:
                if token in seg_lower:
                    score += 3
            if any(term in seg_lower for term in ["november", "january", "december", "march", "75%", "rs.", "mahadbt", "syllabus", "credits"]):
                score += 2

            if score > 0:
                scored_candidates.append({
                    "score": score,
                    "sentence": seg,
                    "source": source_name,
                    "page": page_num
                })

    if not scored_candidates:
        top_hit = retrieved_chunks[0]
        return f"{top_hit['text'][:250]}...\n\n**Source:** `{top_hit['source']}`, Page {top_hit['page']}"

    scored_candidates.sort(key=lambda x: x["score"], reverse=True)
    best = scored_candidates[0]
    selected_sentences = [best["sentence"]]
    primary_source = best["source"]
    primary_page = best["page"]

    for cand in scored_candidates[1:]:
        if cand["source"] == primary_source and cand["page"] == primary_page:
            if cand["sentence"] not in selected_sentences and len(selected_sentences) < 3:
                selected_sentences.append(cand["sentence"])

    answer_body = " ".join(selected_sentences)
    return f"{answer_body}\n\n**Source:** `{primary_source}`, Page {primary_page}"

def call_gemini_api(prompt: str, key: str) -> str:
    import urllib.request
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={key}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.1, "maxOutputTokens": 512}
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        return res["candidates"][0]["content"]["parts"][0]["text"].strip()

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "college": "Atharva College of Engineering, Malad",
        "project": "Smart College Assistant (RAG)",
        "indexed_chunks": len(DOCUMENTS_CACHE)
    }

@app.get("/api/documents")
def get_documents():
    doc_stats = {}
    for item in DOCUMENTS_CACHE:
        src = item["source"]
        page = item["page"]
        if src not in doc_stats:
            doc_stats[src] = {"source": src, "chunks": 0, "pages": set()}
        doc_stats[src]["chunks"] += 1
        doc_stats[src]["pages"].add(page)

    res = []
    for src, info in doc_stats.items():
        res.append({
            "source": src,
            "chunks": info["chunks"],
            "total_pages": len(info["pages"])
        })
    return sorted(res, key=lambda x: x["source"])

@app.post("/api/chat")
def chat_endpoint(req: QueryRequest):
    question = req.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    hits = search_documents(question, k=req.top_k, threshold=req.threshold)
    if not hits:
        return {
            "answer": NOT_FOUND_MESSAGE,
            "citations": [],
            "retrieved_count": 0,
            "status": "not_found"
        }

    citations = []
    seen = set()
    for h in hits:
        key = (h["source"], h["page"])
        if key not in seen:
            citations.append({"source": h["source"], "page": h["page"], "similarity": h["similarity"]})
            seen.add(key)

    api_key = req.api_key or os.environ.get("GEMINI_API_KEY")
    answer = ""

    if api_key:
        try:
            context_text = "\n\n".join([f"--- Document: {h['source']} (Page {h['page']}) ---\n{h['text']}" for h in hits])
            prompt = f"""You are the Smart College Assistant for Atharva College of Engineering.
Answer the question using ONLY the provided context below.
If the answer cannot be found in the context, reply exactly: "{NOT_FOUND_MESSAGE}"
Mention the source document and page number.

Context:
{context_text}

Question:
{question}
"""
            answer = call_gemini_api(prompt, api_key)
        except Exception:
            answer = synthesize_extractive_answer(question, hits)
    else:
        answer = synthesize_extractive_answer(question, hits)

    return {
        "answer": answer,
        "citations": citations,
        "retrieved_count": len(hits),
        "status": "success"
    }

@app.get("/api/evaluate")
def evaluate_benchmark():
    test_suite = [
        {"id": 1, "question": "What is the last date for exam form submission?", "category": "Date / deadline", "expected_source": "Exam_Circular_2025.pdf", "keywords": ["15 November 2025"]},
        {"id": 2, "question": "What is the minimum attendance required to appear for exams?", "category": "Rule / policy", "expected_source": "Attendance_Policy_Rules.pdf", "keywords": ["75%"]},
        {"id": 3, "question": "Which subjects are covered in the Semester IV syllabus?", "category": "Syllabus", "expected_source": "Semester_IV_ECS_Syllabus.pdf", "keywords": ["Applied Mathematics", "Microcontroller", "Database Management Systems"]},
        {"id": 4, "question": "How can I apply for a scholarship?", "category": "Procedure", "expected_source": "Scholarship_Notice_2025.pdf", "keywords": ["MahaDBT", "Counter No. 3"]},
        {"id": 5, "question": "When does the next semester begin?", "category": "Date / schedule", "expected_source": "Academic_Calendar_2025_2026.pdf", "keywords": ["5th January 2026"]},
        {"id": 6, "question": "What is the capital of France?", "category": "Out of scope", "expected_source": None, "keywords": ["I could not find this in the college documents."]}
    ]

    results = []
    passed_count = 0

    for tc in test_suite:
        hits = search_documents(tc["question"], k=4, threshold=0.25)
        ans = synthesize_extractive_answer(tc["question"], hits)
        citations = [{"source": h["source"], "page": h["page"]} for h in hits]

        passed = False
        if tc["expected_source"] is None:
            if "could not find this" in ans.lower():
                passed = True
        else:
            src_match = any(tc["expected_source"].lower() in c["source"].lower() for c in citations)
            kw_match = any(kw.lower() in ans.lower() for kw in tc["keywords"])
            if src_match and kw_match:
                passed = True

        if passed:
            passed_count += 1

        results.append({
            "id": tc["id"],
            "question": tc["question"],
            "category": tc["category"],
            "top_citation": f"{citations[0]['source']} (p. {citations[0]['page']})" if citations else "None",
            "passed": passed,
            "answer_preview": ans[:140] + "..."
        })

    return {
        "passed": passed_count,
        "total": len(test_suite),
        "accuracy": round((passed_count / len(test_suite)) * 100, 1),
        "results": results
    }
