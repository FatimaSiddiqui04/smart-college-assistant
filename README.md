# 🎓 Smart College Assistant: An AI-Powered Chatbot for Academic Document Retrieval (RAG-Based)

**Mini Project 1A (2020 ‘NEP’ Scheme)**  
**Second Year, Semester III (SE Sem-III)**  
**Department of Electronics & Computer Science (ECS)**  
**Atharva College of Engineering, Malad**  
**University of Mumbai — Academic Year 2025–2026**

---

### 👥 Project Team:
1. **Atharva Kanade**
2. **Fatima Siddiqui**
3. **Prasad Kalaskar**
4. **Zennerah Shaikh**

**Project Guide:** **Dr. Tejaswini Jadhav** (Head of Department, ECS)  
**Principal:** **Dr. Ramesh Kulkarni**

---

## 📌 1. Project Overview

The **Smart College Assistant** is a document-grounded chatbot designed to solve information fragmentation in academic institutions. Official college notices, examination circulars, fee rules, timetables, and syllabi are typically scattered across PDF circulars, notice boards, and messaging groups.

Using **Retrieval-Augmented Generation (RAG)**, the assistant allows students and faculty to ask questions in plain English and receive instant, verifiable answers backed by exact source citations (Document Name and Page Number).

### 🎯 Key Project Objectives:
- **Zero Hallucination:** Strict grounding on retrieved college passages.
- **Source Verification:** Every answer displays the document name and page number.
- **Out-of-Scope Handling:** Directly answers *"I could not find this in the college documents."* when information is absent.
- **No Model Retraining:** New circulars and syllabi are added dynamically via document upload.
- **Low Cost & Privacy:** Runs on an ordinary laptop with local embeddings and a persistent vector database.

---

## 🏗️ 2. System Architecture

The system implements the two core pipelines detailed in Chapter 4 of the project report:

```
A. INDEXING PIPELINE (Offline / Document Ingestion)
[College Documents (PDF / DOCX)]
              ↓
[Text Extraction & Cleaning (PyPDF / python-docx)]
              ↓
[Overlapping Chunking (800 chars, 150 overlap)]
              ↓
[Embedding Generation (Sentence-Transformers: all-MiniLM-L6-v2, 384 dimensions)]
              ↓
[ChromaDB Persistent Vector Store (Cosine Similarity Metric)]

B. QUERY PIPELINE (Online / Real-Time Student Question Answering)
[Student Question]
              ↓
[Query Embedding (all-MiniLM-L6-v2)]
              ↓
[Top-K Nearest Neighbor Cosine Retrieval (ChromaDB)]
              ↓
[Similarity Threshold Check (Score >= 0.30)]
       ├── (Below Threshold) ──> Return "I could not find this in the college documents."
       └── (Above Threshold) ──> [Prompt Builder (Rules + Context + Question)]
                                                ↓
                                    [LLM Generation (Temp = 0.1)]
                                                ↓
                                    [Answer with Document & Page Citation]
```

---

## 💻 3. Technology Stack

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Language** | Python 3.9+ / 3.10+ | Core pipeline and API integration |
| **Document Loader** | `pypdf`, `python-docx` | Page-wise text extraction and metadata preservation |
| **Vector Embedding** | `all-MiniLM-L6-v2` (`sentence-transformers`) | Converts text to 384-dimensional dense vectors |
| **Vector Database** | `ChromaDB` (Persistent) | Local nearest-neighbor semantic search (cosine space) |
| **LLM Generation** | Google Gemini / Groq / Ollama / Built-in Extractor | Synthesizes grounded natural language responses |
| **User Interface** | `Streamlit` | Web interface for student chat, admin ingestion, and evaluation |

---

## 🚀 4. Quick Start & Execution

### Option A: 1-Click Launch (Windows)
Double-click `run.bat` in this folder. It will launch the Streamlit application in your default web browser.

### Option B: Terminal Command
```bash
# Navigate to the project directory
cd smart-college-assistant

# Install dependencies (if not already installed)
pip install -r requirements.txt

# Launch the Streamlit application
streamlit run app.py
```
Open **`http://localhost:8501`** in your browser.

---

## 📂 5. Pre-Loaded Sample College Documents

The application includes 5 authentic sample documents matching the test cases from **Page 28** of the report:

1. **`Exam_Circular_2025.pdf`**: Exam form submission deadline (15 November 2025 without late fee), late fee penalties, and hall ticket dates.
2. **`Attendance_Policy_Rules.pdf`**: Ordinance 6086 compliance, 75% mandatory attendance rule, condonation policy (60%), and debarment consequences.
3. **`Semester_IV_ECS_Syllabus.pdf`**: Curriculum scheme and subject list (Applied Maths IV, Microcontrollers, DBMS, Communication Engineering, Signal Processing, Mini Project 1B).
4. **`Scholarship_Notice_2025.pdf`**: Government of Maharashtra MahaDBT portal scholarship procedures, EBC waiver, required documents, and Counter No. 3 submission.
5. **`Academic_Calendar_2025_2026.pdf`**: Next semester commencement date (5th January 2026), mid-term exams, Techithon fest, and vacations.

*To index these into ChromaDB instantly, simply click the **"📥 Index Sample Documents"** button in the sidebar or run:*
```bash
python generate_sample_docs.py
python test_rag.py
```

---

## 🧪 6. Evaluation Benchmark Results (Report Page 28)

Running `python test_rag.py` executes the 6 evaluation benchmark queries specified in the report:

| No. | Question | Category | Expected Result | Actual System Output | Status |
| :---: | :--- | :--- | :--- | :--- | :---: |
| **1** | What is the last date for exam form submission? | Date / deadline | 15 November 2025 | 15 November 2025 (`Exam_Circular_2025.pdf`, Page 2) | **PASS ✅** |
| **2** | What is the minimum attendance required to appear for exams? | Rule / policy | 75% | 75% (`Attendance_Policy_Rules.pdf`, Page 1) | **PASS ✅** |
| **3** | Which subjects are covered in the Semester IV syllabus? | Syllabus | Applied Maths IV, Microcontrollers, DBMS, etc. | Applied Maths, Microcontrollers, DBMS (`Semester_IV_ECS_Syllabus.pdf`, Page 1) | **PASS ✅** |
| **4** | How can I apply for a scholarship? | Procedure | MahaDBT registration & Counter 3 | Step-by-step MahaDBT portal steps (`Scholarship_Notice_2025.pdf`, Page 1) | **PASS ✅** |
| **5** | When does the next semester begin? | Date / schedule | 5th January 2026 | 5th January 2026 (`Academic_Calendar_2025_2026.pdf`, Page 2) | **PASS ✅** |
| **6** | What is the capital of France? | Out of scope | "I could not find this..." | "I could not find this in the college documents." | **PASS ✅** |

**Benchmark Accuracy: 6/6 (100% Pass Rate)**

---

## 📁 7. Project File Structure

```
smart-college-assistant/
├── app.py                      # Interactive Streamlit Web UI (Chat, Admin, Evaluation, Viva Guide)
├── rag_pipeline.py             # Core RAG Pipeline (ChromaDB, top-k retrieval, threshold filtering)
├── document_loader.py          # PDF & DOCX loaders with character chunking & overlap
├── embeddings.py               # SentenceTransformer (all-MiniLM-L6-v2) embedding module
├── llm_client.py               # Multi-provider LLM connector (Gemini, Groq, Ollama, OpenAI, Offline)
├── rag_config.py               # Hyperparameters, directories, and prompt templates
├── generate_sample_docs.py     # Script that builds the authentic college sample PDFs
├── test_rag.py                 # Automated test runner for the 6 evaluation questions
├── requirements.txt            # Python dependencies
├── run.bat                     # Windows 1-click startup batch script
├── .env.example                # Environment variables template for API keys
├── .env                        # Local configuration
├── chroma_store/               # Persistent ChromaDB vector database files
├── sample_documents/           # 5 pre-loaded sample college PDF circulars
└── uploaded_documents/         # User uploaded PDF and DOCX files
```

---

## 🎓 8. Viva Voce Q&A Preparation

**Q1: What is the primary difference between RAG and Fine-Tuning?**  
*Answer:* Fine-tuning changes model weights, which is computationally expensive and cannot cite sources. When college circulars update each semester, a fine-tuned model would require retraining. In RAG, external knowledge is stored in a vector database; new circulars are indexed in seconds with zero model retraining, and every answer cites the exact document and page number.

**Q2: Why use Cosine Similarity instead of Euclidean Distance?**  
*Answer:* Cosine similarity evaluates the cosine of the angle between two embedding vectors ($\cos \theta = \frac{\mathbf{u} \cdot \mathbf{v}}{\|\mathbf{u}\| \|\mathbf{v}\|}$), measuring thematic and semantic similarity independent of text length.

**Q3: How does the system prevent AI hallucination?**  
*Answer:* Two mechanisms: (1) A strict prompt instruction commanding the model to answer ONLY from the supplied context, and (2) A cosine similarity threshold (0.30) that rejects irrelevant results and replies *"I could not find this in the college documents."* for out-of-scope questions.

**Q4: Can this system run completely offline?**  
*Answer:* Yes! The embedding model (`all-MiniLM-L6-v2`) and the vector database (`ChromaDB`) run entirely on the local CPU. For generation, the system supports local models via **Ollama** or the built-in **Offline Extractive Synthesizer**, requiring zero internet connection during college demonstrations.
