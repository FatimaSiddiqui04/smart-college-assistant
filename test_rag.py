"""
End-to-End Test and Verification Script
Indexes sample PDFs into ChromaDB and runs all 6 test questions from Page 28 of the project report:
1. What is the last date for exam form submission?
2. What is the minimum attendance required to appear for exams?
3. Which subjects are covered in the Semester IV syllabus?
4. How can I apply for a scholarship?
5. When does the next semester begin?
6. What is the capital of France? (Out of scope test)
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from rag_pipeline import CollegeRAGPipeline
from llm_client import generate_rag_response

def main():
    print("=" * 70)
    print("SMART COLLEGE ASSISTANT - VERIFICATION & EVALUATION RUN")
    print("Atharva College of Engineering - SE Sem-III Mini Project 1A")
    print("=" * 70)

    pipeline = CollegeRAGPipeline()
    
    print("\n1. Indexing sample college documents...")
    res = pipeline.index_all_sample_documents()
    for doc, chunks in res.items():
        print(f"   Indexed: {doc} ({chunks} chunks)")

    print(f"\nTotal indexed documents in ChromaDB: {len(pipeline.get_indexed_documents())}")
    print(f"Total chunks in collection: {pipeline.collection.count()}")

    # Test questions from Page 28
    test_suite = [
        {
            "id": 1,
            "question": "What is the last date for exam form submission?",
            "category": "Date / deadline",
            "expected_source": "Exam_Circular_2025.pdf",
            "expected_keywords": ["15 November 2025"]
        },
        {
            "id": 2,
            "question": "What is the minimum attendance required to appear for exams?",
            "category": "Rule / policy",
            "expected_source": "Attendance_Policy_Rules.pdf",
            "expected_keywords": ["75%"]
        },
        {
            "id": 3,
            "question": "Which subjects are covered in the Semester IV syllabus?",
            "category": "Syllabus",
            "expected_source": "Semester_IV_ECS_Syllabus.pdf",
            "expected_keywords": ["Applied Mathematics", "Microcontroller", "Database Management Systems"]
        },
        {
            "id": 4,
            "question": "How can I apply for a scholarship?",
            "category": "Procedure",
            "expected_source": "Scholarship_Notice_2025.pdf",
            "expected_keywords": ["MahaDBT", "Counter No. 3"]
        },
        {
            "id": 5,
            "question": "When does the next semester begin?",
            "category": "Date / schedule",
            "expected_source": "Academic_Calendar_2025_2026.pdf",
            "expected_keywords": ["5th January 2026"]
        },
        {
            "id": 6,
            "question": "What is the capital of France?",
            "category": "Out of scope (expect 'not found')",
            "expected_source": None,
            "expected_keywords": ["I could not find this in the college documents."]
        }
    ]

    print("\n" + "=" * 70)
    print("RUNNING 6 EVALUATION TEST CASES")
    print("=" * 70)

    passed_count = 0

    for test in test_suite:
        q_id = test["id"]
        q = test["question"]
        cat = test["category"]
        
        print(f"\n[Test #{q_id}] Question: {q}")
        print(f"Category: {cat}")
        
        # Retrieve chunks
        hits = pipeline.retrieve(q, k=4, threshold=0.30)
        resp = generate_rag_response(q, hits, provider="Offline Extractor")
        
        answer = resp["answer"]
        citations = resp["citations"]
        
        print(f"Top Retrieved Chunks: {len(hits)}")
        if citations:
            print(f"Primary Citation: {citations[0]['source']}, Page {citations[0]['page']} (Similarity: {citations[0]['similarity']})")
        print(f"Answer Output:\n{answer}")
        
        # Verification
        passed = False
        if test["expected_source"] is None:
            # Out of scope query should produce not found
            if "could not find this" in answer.lower():
                passed = True
        else:
            # Check source and keywords
            source_matched = any(test["expected_source"].lower() in c["source"].lower() for c in citations)
            keyword_matched = any(kw.lower() in answer.lower() for kw in test["expected_keywords"])
            if source_matched and keyword_matched:
                passed = True

        status_str = "PASS [OK]" if passed else "CHECK [REVIEW]"
        if passed:
            passed_count += 1
        print(f"Result: {status_str}")

    print("\n" + "=" * 70)
    print(f"EVALUATION COMPLETE: {passed_count}/{len(test_suite)} Tests Passed Successfully!")
    print("=" * 70)

if __name__ == "__main__":
    main()
