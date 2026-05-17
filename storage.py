import os
import faiss
import numpy as np

USE_OPENAI = os.getenv("USE_OPENAI", "false").lower() == "true"


def embeddings(chunks):

    if not chunks:
        return None, None

    texts = [chunk.page_content for chunk in chunks]

   
    if USE_OPENAI:

        from openai import OpenAI

        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=texts
        )

        embedding_vectors = [
            item.embedding for item in response.data
        ]

        embedding_vectors = np.array(
            embedding_vectors
        ).astype("float32")

        model = "openai"

  
    else:

        from sentence_transformers import SentenceTransformer

        model = SentenceTransformer(
            "sentence-transformers/all-MiniLM-L6-v2"
        )

        embedding_vectors = model.encode(texts)

        embedding_vectors = np.array(
            embedding_vectors
        ).astype("float32")

   
    dimension = embedding_vectors.shape[1]

    index = faiss.IndexFlatL2(dimension)

    index.add(embedding_vectors)

    return index, model
