import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


def embeddings(chunks):
    if not chunks:
        return None, None
    

    texts = [chunk.page_content for chunk in chunks]

    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    model = SentenceTransformer("all-MiniLM-L6-v2", device="cpu")  

    vectors = model.encode(texts, batch_size=16, show_progress_bar=False)
    embeddings = np.array(embeddings).astype("float32")

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    return index,model
