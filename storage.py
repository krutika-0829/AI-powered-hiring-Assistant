import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


def embeddings(chunks):
    if not chunks:
        return None, None
    

    texts = [chunk.page_content for chunk in chunks]

    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2", device="cpu")

    embeddings = model.encode(texts)
    embeddings = np.array(embeddings).astype("float32")

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    return index,model
