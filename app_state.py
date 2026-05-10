from ingestion import run_ingestion
from storage import embeddings

chunks, metadata_store = run_ingestion()
index, model = embeddings(chunks)