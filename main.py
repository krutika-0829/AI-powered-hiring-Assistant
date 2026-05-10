from ingestion import run_ingestion
from storage import embeddings
from retrival import retrieve_chunks, rank_candidates, get_filtered_ids
from llm import QnA
import json


def resume_matching_by_jd(user_input, index, model, chunks, metadata_store):
    jd = user_input.lower().strip()
    results = rank_candidates(jd,index,model,chunks,metadata_store)
    if not results:
        return {"message": "No matching candidates found"}
    return results[:5]



def handle_query(user_input, index, model, chunks, metadata_store):

    text = user_input.lower().strip()

    filtered_ids = get_filtered_ids(user_input,metadata_store)

    retrived_context = retrieve_chunks(user_input,index,model,chunks,k=20)

    final_chunks = []

    for chunk in retrived_context:

            candidate_name = chunk.metadata.get(
                "candidate_name",
                "Unknown Candidate"
            )

            formatted_chunk = f"""
            Candidate Name: {candidate_name}
            Resume Content: {chunk.page_content}
            """

            if not filtered_ids:
                final_chunks.append(formatted_chunk)

            elif chunk.metadata.get("doc_id") in filtered_ids:
                final_chunks.append(formatted_chunk)

            if len(final_chunks) == 5:
                break

        
    if not final_chunks:

        for chunk in retrived_context[:3]:
            candidate_name = chunk.metadata.get("candidate_name","Unknown Candidate")

            formatted_chunk = f"""
            Candidate Name: {candidate_name}
            Resume Content:{chunk.page_content}
            """

            final_chunks.append(formatted_chunk)

       
    context = "\n\n".join(final_chunks)

    Answer = QnA(user_input, context)

    try:
        parsed = json.loads(Answer)
        return parsed

    except:
        return {
            "error": "Invalid JSON",
            "raw": Answer
        }
