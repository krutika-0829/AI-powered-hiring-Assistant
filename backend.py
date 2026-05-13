from fastapi import FastAPI, UploadFile, File,HTTPException
from pydantic import BaseModel,Field
from typing import Annotated
from typing import List
from main import handle_query,resume_matching_by_jd
import shutil
from ingestion import run_ingestion
from storage import embeddings
from fastapi.openapi.utils import get_openapi


index = None
model = None
chunks = None
metadata_store = None

app = FastAPI()
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(
        title="FastAPI",
        version="0.1.0",
        routes=app.routes,
    )
    schema["openapi"] = "3.0.3"
    
    
    for schema_def in schema.get("components", {}).get("schemas", {}).values():
        for field in schema_def.get("properties", {}).values():
            if field.get("type") == "array":
                items = field.get("items", {})
                if "contentMediaType" in items:
                    del items["contentMediaType"]
                    items["type"] = "string"
                    items["format"] = "binary"

    app.openapi_schema = schema
    return app.openapi_schema

app.openapi = custom_openapi


class QueryRequest(BaseModel):
    query: Annotated[str,Field(...,description="Enter your question", example="What are Michelle Lopez's design skills?")]


class JDRequest(BaseModel): 
    text: Annotated[str,Field(...,description="Enter Job Description")]
    

@app.post("/upload_resume")
async def uploadResume(files: Annotated[List[UploadFile], File(description="Upload PDF resumes")]):

    for file in files:
  
        
        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(
                status_code=400,
                detail=f"{file.filename} is not a PDF file"
            )

        file_path = f"docs/{file.filename}"

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

    
    global chunks, metadata_store, index, model

   
    chunks, metadata_store = run_ingestion()
    index, model = embeddings(chunks)


    return {"message": f"{len(files)} resumes uploaded and processed"}

@app.post("/user_query")
def user_query(request : QueryRequest):
    if index is None:
        return {"error": "No resumes uploaded yet"}
    
    user_input = request.query
    result = handle_query(user_input,index,model,chunks,metadata_store)
    return {"result": result}

@app.post("/job_description")
def resume_matching(request : JDRequest):
        if index is None:
           return {"error": "No resumes uploaded yet"}
        
        user_input = request.text
        result =  resume_matching_by_jd(user_input, index, model, chunks, metadata_store)
        return {"result": result}










