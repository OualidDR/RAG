import chromadb
from sentence_transformers import SentenceTransformer
from ingest import process_pdf

model = SentenceTransformer("BAAI/bge-m3")

client = chromadb.PersistentClient(path="chroma_db")
collection = client.get_or_create_collection(
    name="ensias",
    metadata={"hnsw:space": "cosine"},
)

def chunk_id(c):
    title = c["article"] or c["section"] or c["chapter"] or "cover"
    return f"{c['source']}::{title}"

def upsert_chunks(chunks, category):
    ids = [chunk_id(c) for c in chunks]
    assert len(ids) == len(set(ids)), "duplicate ids"
    vectors = model.encode(
        [c["text"] for c in chunks],
        normalize_embeddings=True,
        show_progress_bar=True,
    )
    collection.upsert(
        ids=ids,
        documents=[c["text"] for c in chunks],
        embeddings=vectors.tolist(),
        metadatas=[{
            "source": c["source"],
            "category": category,
            "chapter": c["chapter"],
            "section": c["section"],
            "article": c["article"],
            "page": c["page"],
        } for c in chunks],
    )

if __name__ == "__main__":
    path = "raw_docs/Réglement_Etudes_Cycle_ingénieur_Validée_CE_30_Mars_2026.pdf"
    upsert_chunks(process_pdf(path), "reglement_etudes")
    print("in database:", collection.count())