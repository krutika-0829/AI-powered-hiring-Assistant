import os
import re
import json 
from llm import get_information
from collections import defaultdict
from langchain_core.documents import Document
from langchain_community.document_loaders  import DirectoryLoader,PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


def load_documents(docs_path = "docs"):

  
    if not os.path.exists(docs_path):
       raise FileNotFoundError(f"The directory {docs_path} does not exist.")
    
    
    loader = DirectoryLoader(
    path = docs_path,
    glob="*.pdf",
    loader_cls= PyPDFLoader
    )
    documents = loader.load()
    
    return documents



#this functon cleans Text Content of documents
def clean_text(text):

    # remove weird unicode characters
    text = text.replace("\uf0b7", " ")   
    text = text.replace("\u2022", " ")   
    text = text.replace("\xa0", " ")    

    # remove repeated spaces
    text = re.sub(r"[ \t]+", " ", text)

    # remove repeated blank lines
    text = re.sub(r"\n\s*\n+", "\n\n", text)

    # trim overall whitespace
    text = text.strip()

    return text



def cleaned_docs(documents):
  cleaned_docs = []
  for doc in documents:

    doc_id = doc.metadata["source"]
    cleaned_text = clean_text(doc.page_content)
    
    cleaned_doc = Document(
        id = doc_id,
        page_content=cleaned_text,
        metadata={
           **doc.metadata,
           "doc_id": doc_id
    }
    )

    cleaned_docs.append(cleaned_doc)
  return cleaned_docs
  
  
def grouped_docs_per_resume(cleaned_docs):
   grouped_docs = defaultdict(list) 
   for doc in cleaned_docs : 
        source = doc.metadata["source"]
        grouped_docs[source].append(doc.page_content) 
   return grouped_docs


def info_of_applicants(context):
    
     result = get_information(context)
     try: 
        parsed = json.loads(result)
        return parsed 
     except: 
         return {"error": "Invalid JSON", "raw": result}
     

def extract_metadata(grouped_docs):
        results = []
        for file, pages in grouped_docs.items():
            print(f"Processing: {file}")
            full_text = " ".join(pages)
            metadata = info_of_applicants(full_text)
            metadata['source'] = file
            results.append(metadata)
    
        with open("results.json", "w") as f:
             json.dump(results, f)
        print("Done! Saved to cache.")
        return results


def chunking(cleaned_docs):
    splitter = RecursiveCharacterTextSplitter(
    chunk_size=400,
    chunk_overlap=80
    )
    chunks = splitter.split_documents(cleaned_docs) 
 
    return chunks


def metadata_storage(chunks,results):
    metadata_lookup = {r['source']: r for r in results} 
    metadata_store = {}
    for chunk in chunks:
        source = chunk.metadata.get("source")
        info = metadata_lookup.get(source, {})
        chunk.metadata["candidate_name"] = info.get("Name")

        doc_id = chunk.metadata.get("doc_id")
        

        skills = info.get("Skills", [])
        if isinstance(skills, str):
            skills = [s.strip() for s in skills.split(",")]

        metadata_store[doc_id] = {
            "name": info.get("Name"),
            "skills": skills,
            "role": info.get("Role"),
            "experience": info.get("Experience"),
            "projects": info.get("Projects", []),
            "education": info.get("Education"),
            "source": source
    }
     
    return metadata_store,chunks
        

def run_ingestion():
   
    if os.path.exists("results.json"):     
        os.remove("results.json")
    
    documents = load_documents("docs")
    

    cleaned_documents = cleaned_docs(documents)

    grouped_documents = grouped_docs_per_resume(cleaned_documents)

    results = extract_metadata(grouped_documents)

    chunks = chunking(cleaned_documents)

    metadata_store, chunks = metadata_storage(chunks, results)

    with open("metadata_store.json", "w") as f:
        json.dump(metadata_store, f)

    print("Ingestion pipeline completed successfully!")

    return chunks, metadata_store

    
if __name__ == "__main__":
   run_ingestion()
