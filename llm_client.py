"""
LLM Integration Module for Smart College Assistant
Supports multiple LLM backends:
1. Google Gemini API (gemini-2.5-flash, gemini-1.5-flash)
2. Groq API (llama-3.3-70b-versatile, llama-3.1-8b-instant)
3. Ollama (Local open-source models, e.g., llama3, mistral)
4. OpenAI API (gpt-4o-mini, gpt-3.5-turbo)
5. Built-in Offline Extractive Generator (Instant, reliable fallback for offline demos & vivas)
"""

import os
import re
import json
import urllib.request
import urllib.error
from typing import Dict, Any, List, Optional

import rag_config as config

def call_gemini(prompt: str, api_key: str, model_name: str = "gemini-2.5-flash", temperature: float = config.DEFAULT_LLM_TEMPERATURE) -> str:
    """
    Invokes Google Gemini API via official google-genai library or direct REST fallback.
    """
    try:
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=temperature,
                max_output_tokens=config.MAX_RESPONSE_TOKENS
            )
        )
        return response.text.strip()
    except Exception as e:
        # Direct REST API fallback
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": config.MAX_RESPONSE_TOKENS
            }
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            res_json = json.loads(resp.read().decode("utf-8"))
            return res_json["candidates"][0]["content"]["parts"][0]["text"].strip()

def call_groq(prompt: str, api_key: str, model_name: str = "llama-3.3-70b-versatile", temperature: float = config.DEFAULT_LLM_TEMPERATURE) -> str:
    """
    Invokes Groq Cloud API for ultra-fast Llama 3 inference.
    """
    from groq import Groq
    client = Groq(api_key=api_key)
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "user", "content": prompt}
        ],
        model=model_name,
        temperature=temperature,
        max_tokens=config.MAX_RESPONSE_TOKENS
    )
    return chat_completion.choices[0].message.content.strip()

def call_ollama(prompt: str, base_url: str = "http://localhost:11434", model_name: str = "llama3", temperature: float = config.DEFAULT_LLM_TEMPERATURE) -> str:
    """
    Invokes a local Ollama instance for complete offline local LLM privacy.
    """
    url = f"{base_url.rstrip('/')}/api/generate"
    payload = {
        "model": model_name,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_predict": config.MAX_RESPONSE_TOKENS
        }
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=45) as resp:
        res_json = json.loads(resp.read().decode("utf-8"))
        return res_json.get("response", "").strip()

def call_openai(prompt: str, api_key: str, model_name: str = "gpt-4o-mini", temperature: float = config.DEFAULT_LLM_TEMPERATURE) -> str:
    """
    Invokes OpenAI Chat Completion API.
    """
    url = "https://api.openai.com/v1/chat/completions"
    payload = {
        "model": model_name,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "max_tokens": config.MAX_RESPONSE_TOKENS
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        res_json = json.loads(resp.read().decode("utf-8"))
        return res_json["choices"][0]["message"]["content"].strip()

def offline_extractive_answer(question: str, retrieved_chunks: List[Dict[str, Any]]) -> str:
    """
    High-precision extractive synthesizer for offline demonstrations.
    Scans across ALL retrieved chunks, evaluates sentence relevance and information density,
    synthesizes a direct factual answer, and cites the specific source document and page number.
    """
    if not retrieved_chunks:
        return config.NOT_FOUND_MESSAGE

    # Clean question query tokens
    stop_words = {"what", "is", "the", "for", "to", "in", "which", "are", "of", "a", "an", "and", "do", "does", "how", "can", "i", "when"}
    raw_tokens = re.findall(r'\b[a-zA-Z0-9_\-\.%]+\b', question.lower())
    content_tokens = [t for t in raw_tokens if t not in stop_words and len(t) > 1]
    
    scored_candidates = []

    for hit in retrieved_chunks:
        source_name = hit.get("source", "College Document")
        page_num = hit.get("page", 1)
        text = hit.get("text", "")

        # Split text into sentences and structured lines
        segments = [s.strip() for s in re.split(r'(?<=[.!?\n])\s+', text) if len(s.strip()) > 15]

        for seg in segments:
            seg_lower = seg.lower()
            # Calculate match score
            score = 0
            for token in content_tokens:
                if token in seg_lower:
                    score += 3
            # Bonus for numerical/date/fee/deadline indicators
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

    # Sort descending by relevance score
    scored_candidates.sort(key=lambda x: x["score"], reverse=True)
    best = scored_candidates[0]
    
    # Check if there is another complementary high-score sentence from the same source
    selected_sentences = [best["sentence"]]
    primary_source = best["source"]
    primary_page = best["page"]

    for cand in scored_candidates[1:]:
        if cand["source"] == primary_source and cand["page"] == primary_page:
            if cand["sentence"] not in selected_sentences and len(selected_sentences) < 3:
                selected_sentences.append(cand["sentence"])

    answer_body = " ".join(selected_sentences)
    formatted_answer = f"{answer_body}\n\n**Source:** `{primary_source}`, Page {primary_page}"
    return formatted_answer

def generate_rag_response(
    question: str,
    retrieved_chunks: List[Dict[str, Any]],
    provider: str = "Offline Extractor",
    api_key: Optional[str] = None,
    model_name: Optional[str] = None,
    ollama_url: str = "http://localhost:11434",
    temperature: float = config.DEFAULT_LLM_TEMPERATURE
) -> Dict[str, Any]:
    """
    Master function to produce answers given retrieved chunks and selected LLM backend.
    Enforces strict grounding and the standard 'not found' behavior.
    """
    # If no chunks passed the similarity threshold, return 'not found' immediately
    if not retrieved_chunks:
        return {
            "answer": config.NOT_FOUND_MESSAGE,
            "citations": [],
            "retrieved_count": 0,
            "status": "not_found"
        }

    # Format citations list
    citations = []
    seen = set()
    for h in retrieved_chunks:
        key = (h["source"], h["page"])
        if key not in seen:
            citations.append({"source": h["source"], "page": h["page"], "similarity": h["similarity"]})
            seen.add(key)

    # Build prompt context
    context_text = "\n\n".join([
        f"--- Document: {h['source']} (Page {h['page']}) ---\n{h['text']}"
        for h in retrieved_chunks
    ])

    prompt = config.RAG_SYSTEM_PROMPT.format(
        not_found_message=config.NOT_FOUND_MESSAGE,
        context=context_text,
        question=question
    )

    answer = ""
    error_msg = None

    try:
        if provider == "Google Gemini":
            key = api_key or os.environ.get("GEMINI_API_KEY")
            if not key:
                raise ValueError("Gemini API Key is required. Please enter it in the sidebar or set GEMINI_API_KEY.")
            model = model_name or "gemini-2.5-flash"
            answer = call_gemini(prompt, api_key=key, model_name=model, temperature=temperature)

        elif provider == "Groq":
            key = api_key or os.environ.get("GROQ_API_KEY")
            if not key:
                raise ValueError("Groq API Key is required. Please enter it in the sidebar or set GROQ_API_KEY.")
            model = model_name or "llama-3.3-70b-versatile"
            answer = call_groq(prompt, api_key=key, model_name=model, temperature=temperature)

        elif provider == "Ollama (Local)":
            model = model_name or "llama3"
            answer = call_ollama(prompt, base_url=ollama_url, model_name=model, temperature=temperature)

        elif provider == "OpenAI":
            key = api_key or os.environ.get("OPENAI_API_KEY")
            if not key:
                raise ValueError("OpenAI API Key is required. Please enter it in the sidebar or set OPENAI_API_KEY.")
            model = model_name or "gpt-4o-mini"
            answer = call_openai(prompt, api_key=key, model_name=model, temperature=temperature)

        else:
            # Offline Extractor
            answer = offline_extractive_answer(question, retrieved_chunks)

    except Exception as e:
        error_msg = str(e)
        # Gracefully fall back to offline extraction so user is never left stranded
        fallback = offline_extractive_answer(question, retrieved_chunks)
        answer = f"*(Notice: {provider} call encountered an error: {error_msg}. Generated using built-in offline extractor)*\n\n{fallback}"

    return {
        "answer": answer,
        "citations": citations,
        "retrieved_count": len(retrieved_chunks),
        "status": "success",
        "error": error_msg
    }
