from pathlib import Path
from sentence_transformers import SentenceTransformer
import faiss 
import numpy as np 
from groq import Groq


model = SentenceTransformer("all-MiniLM-L6-v2")


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

def embed_texts(texts) :
    return model.encode(texts, normalize_embeddings = True)

def build_index (vectors):
    index = faiss.IndexFlatIP(vectors.shape[1])
    index.add(vectors.astype(np.float32))
    return index 


def retrieve(question, index, chunks, k = 2) :
    q  = embed_texts([question]).astype(np.float32)
    scores, ids = index.search(q,k)
    results = []
    for score, i in zip(scores[0], ids[0]) :
        results.append({"text": chunks[i], "score": float(score)})
    return results

def build_pipeline(folder="docs"):
    all_chunks = []
    for name, text in load_documents(folder):
        all_chunks.extend(chunk_text(text))
    vectors = embed_texts(all_chunks)
    index = build_index(vectors)
    return index, all_chunks


def generate_answer(question, results):
    context = "\n\n".join(
        f"[{i+1}] {r['text']}" for i, r in enumerate(results)
    )

    system = (
        "You answer questions using ONLY the context provided. "
        "If the answer is not in the context, say you don't know. "
        "Cite sources like [1]."

    )
    client = Groq()
    response = client.chat.completions.create(
    model="openai/gpt-oss-20b",
    messages=[
        {"role": "system", "content": system},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"},
        ],
    )
    return response.choices[0].message.content

if __name__ == "__main__":
    docs = load_documents("docs")
    all_chunks = []
    for name, text in docs :
        all_chunks.extend(chunk_text(text))

    vectors = embed_texts(all_chunks)
    index = build_index(vectors)

    question = "What is the capital of France?"
    results = retrieve(question, index, all_chunks, k=2)
    answer = generate_answer(question, results)
    print("ANSWER:", answer)


   





























































