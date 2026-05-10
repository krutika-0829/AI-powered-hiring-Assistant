# AI Powered Hiring Assistant

An intelligent resume screening system built with RAG (Retrieval-Augmented Generation). It allows recruiters to upload resumes, ask questions about candidates, and match candidates to job descriptions automatically.



## Features

- Upload multiple PDF resumes
- Ask natural language questions about candidates
- Match candidates to a job description with scoring
- Metadata extraction (name, skills, role, experience, education, projects)
- Semantic search using FAISS + Sentence Transformers
- LLM-powered answers using Mistral via Ollama



## Tech Stack


 LLM | Mistral (via Ollama) |
 Embeddings | Sentence Transformers (all-MiniLM-L6-v2) |
 Vector Store | FAISS |
 PDF Parsing | LangChain + PyPDFLoader |
 Backend | FastAPI |
 Frontend | Streamlit |



## Project Structure


ingestion.py       # PDF loading, cleaning, chunking, metadata extraction
storage.py         # Embedding generation and FAISS index creation
retrival.py        # Semantic search, filtering, candidate ranking
main.py            # Core query handling and JD matching logic
llm.py             # Ollama/Mistral API calls and prompt templates
app_state.py       # Loads index and chunks on startup
backend.py         # FastAPI routes
frontend.py        # Streamlit UI
README.md


## Setup Instructions

### 1. Prerequisites

- Python 3.10+
- [Ollama](https://ollama.com/) installed and running
- Mistral model pulled:

ollama pull mistral

### 2. Install dependencies


pip install -r requirements.txt


### 3. Create docs folder


mkdir docs

Place your resume PDFs inside the `docs/` folder.

### 4. Run the backend


uvicorn backend:app --reload


### 5. Run the frontend

Open a new terminal and run:

streamlit run frontend.py




## API Endpoints


`/upload_resume` Upload one or more PDF resumes 
`/user_query` Ask a question about candidates 
`/job_description` Match candidates to a job description 



## How It Works

1. **Ingestion** — PDFs are loaded, cleaned, and split into chunks
2. **Metadata Extraction** — Mistral extracts name, skills, role, experience, projects, education from each resume
3. **Embedding** — Chunks are embedded using Sentence Transformers and stored in FAISS
4. **Retrieval** — On query, relevant chunks are retrieved semantically + filtered by metadata
5. **Answer Generation** — Retrieved context is passed to Mistral to generate a final answer



## Problems Faced & Solutions

### LLM taking too long on every startup
Mistral was re-processing all resumes on every run which made startup extremely slow. 

**Solution:** Added `results.json` as a cache file. Metadata is extracted once and saved to disk. On next run it loads from cache instead of calling the LLM again. On new resume upload, the cache is automatically deleted and re-generated.

### OpenAPI version mismatch in backend
FastAPI was generating OpenAPI schema version `3.1.0` which caused compatibility issues with some API clients.

**Solution:** Added a custom `custom_openapi()` function in `backend.py` that forces the schema version to `3.0.3` and also fixes array field formats for file uploads.

### Mistral returning inconsistent JSON
Mistral would sometimes wrap JSON in markdown code fences (` ```json ``` `) or return nested dicts instead of plain strings, causing `json.loads` and `.lower()` crashes throughout the pipeline.

**Solution:** Added a `clean_llm_json()` function in `llm.py` that strips markdown fences before parsing, and a `safe_str()` helper in `retrival.py` that safely flattens any value (dict, list, string, None) into a plain string before comparison.

### Irrelevant candidates appearing in JD matching
FAISS always returns the closest chunks even when there is no real match, causing unrelated candidates to appear in results with low but non-zero scores.

**Solution:** Added a minimum score threshold in `rank_candidates()`. Candidates with a score of 1 or less (meaning only FAISS matched, no metadata/skill overlap) are filtered out. If no candidates meet the threshold, the system returns a "No matching candidates found" message instead of showing irrelevant results.


## Notes

- `results.json` and `metadata_store.json` are excluded from the repo (see `.gitignore`) — they are auto-generated on first run
- `docs/` folder is also excluded — add your own resume PDFs locally
- Ollama must be running locally before starting the backend
