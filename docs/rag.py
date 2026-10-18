from pathlib import Path
from sentence_transformers import SentenceTransformer


model = SentenceTransformer("all-MiniLM-L6-v2")

def embed_texts(texts) :
    return model.encode(texts, normalize_embeddings = True)

def load_documents(folder) :
    docs = []
    for path in Path(folder).glob("*.md") :
        text = path.read_text(encoding= "utf-8")
        docs.append((path.name, text))
    return docs

def chunk_text(text, size = 300, overlap = 50 ) :

    text = " ".join(text.split())
    chunks = []
    start = 0
    while start < len(text) :
        chunks.append(text[start:start+size])
        start += size - overlap 
    return chunks 


if __name__ == "__main__":
    docs = load_documents("docs")
    all_chunks = []
    for name, text in docs :
        all_chunks.extend(chunk_text(text))

    vectors = embed_texts(all_chunks)
    print("chunks:", len(all_chunks))
    print("vectors shape:", vectors.shape)
    print("first 5 numbers of vector 0:", vectors[0][:5])
    a, b, c = embed_texts([
        "How many vacation days do I get?",
        "Every full-time employee receives 18 days of paid vacation per year.",
        "The fire extinguisher is located behind the counter.",
    ])
    print("question vs vacation sentence:", a @ b)
    print("question vs fire sentence:    ", a @ c)

   





























































