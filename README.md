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



## Notes

- `results.json` and `metadata_store.json` are excluded from the repo (see `.gitignore`) — they are auto-generated on first run
- `docs/` folder is also excluded — add your own resume PDFs locally
- Ollama must be running locally before starting the backend
