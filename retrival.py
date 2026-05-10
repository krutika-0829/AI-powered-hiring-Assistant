import json
import numpy as np
from collections import defaultdict
from llm import query_filter 


def safe_str(value):
    """Flatten whatever Mistral returns into a plain string."""
    if value is None:
        return ""
    if isinstance(value, dict):
        return " ".join(str(v) for v in value.values())
    if isinstance(value, list):
        return " ".join(str(v) for v in value)
    return str(value)


def retrieve_chunks(user_query, index, model, chunks, k):

    if isinstance(user_query, dict):
        user_query = user_query.get("answer") or user_query.get("query") or str(user_query)
    if isinstance(user_query, list):
        user_query = " ".join(user_query)

    query_embedding = model.encode([user_query])
    query_embedding = np.array(query_embedding).astype("float32")

    distances, indices = index.search(query_embedding, k)
    retrieved_chunks = [chunks[i] for i in indices[0]]
    return retrieved_chunks


def get_filtered_ids(query, metadata_store):

    filters = query_filter(query)

    try:
        filters = json.loads(filters)
    except:
        filters = {}

    results = []

    for doc_id, meta in metadata_store.items():

        score = 0

        query_skills = filters.get("skills") or []
        if isinstance(query_skills, str):
            query_skills = [query_skills]
        doc_skills = [s.lower() for s in meta.get("skills", [])]

        for skill in query_skills:
            if safe_str(skill).lower() in doc_skills:
                score += 3

        query_projects = filters.get("projects") or []
        if isinstance(query_projects, str):
            query_projects = [query_projects]
        doc_projects = [p.lower() for p in meta.get("projects", [])]

        for project in query_projects:
            for doc_project in doc_projects:
                if safe_str(project).lower() in doc_project:
                    score += 2

        query_role = safe_str(filters.get("role")).lower()
        doc_role = safe_str(meta.get("role")).lower()

        if query_role and query_role in doc_role:
            score += 2

        if score > 0:
            results.append((doc_id, score))

    results.sort(key=lambda x: x[1], reverse=True)
    return [doc_id for doc_id, _ in results[:20]]


def rank_candidates(job_description, index, model, chunks, metadata_store, top_k_chunks=20):

    retrieved_chunks = retrieve_chunks(job_description, index, model, chunks, k=top_k_chunks)

    candidate_scores = defaultdict(float)

    for chunk in retrieved_chunks:
        doc_id = chunk.metadata.get("doc_id")
        if doc_id:
            candidate_scores[doc_id] += 1

    filters = query_filter(job_description)

    try:
        filters = json.loads(filters)
    except:
        filters = {}

    jd_skills = filters.get("skills") or []
    if isinstance(jd_skills, str):
        jd_skills = [jd_skills]

    for doc_id, meta in metadata_store.items():

        doc_skills = [s.lower() for s in meta.get("skills", [])]
        for skill in jd_skills:
            if safe_str(skill).lower() in doc_skills:
                candidate_scores[doc_id] += 3

        query_role = safe_str(filters.get("role")).lower()
        doc_role = safe_str(meta.get("role")).lower()
        if query_role and query_role in doc_role:
            candidate_scores[doc_id] += 2

        query_projects = filters.get("projects") or []
        if isinstance(query_projects, str):
            query_projects = [query_projects]
        doc_projects = [p.lower() for p in meta.get("projects", [])]
        for project in query_projects:
            for doc_project in doc_projects:
                if safe_str(project).lower() in doc_project:
                    candidate_scores[doc_id] += 2

        query_education = safe_str(filters.get("education")).lower()
        doc_education = safe_str(meta.get("education")).lower()
        if query_education and query_education in doc_education:
            candidate_scores[doc_id] += 1

    ranked = sorted(candidate_scores.items(), key=lambda x: x[1], reverse=True)
    
    Min_score = 3
    results = []
    for doc_id, score in ranked:
        if score <= 1:      
            continue 
        meta = metadata_store.get(doc_id, {})
        results.append({
            "name": meta.get("name"),
            "score": score,
            "skills": meta.get("skills"),
            "role": meta.get("role"),
            "source": meta.get("source")
        })

    return results[:5]