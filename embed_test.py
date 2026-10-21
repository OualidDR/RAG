import numpy as np
from sentence_transformers import SentenceTransformer
from ingest import process_pdf

model = SentenceTransformer("BAAI/bge-m3")
print("max tokens:", model.max_seq_length)

chunks = process_pdf("raw_docs/Réglement_Etudes_Cycle_ingénieur_Validée_CE_30_Mars_2026.pdf")
vectors = model.encode([c["text"] for c in chunks],
                       normalize_embeddings=True, show_progress_bar=True)

def ask(question, k=3):
    q = model.encode([question], normalize_embeddings=True)[0]
    scores = vectors @ q
    print("\n", question)
    for i in np.argsort(-scores)[:k]:
        c = chunks[i]
        title = c["article"] or c["section"] or c["chapter"]
        print(f"  {scores[i]:.2f} | {title[:60]} | page {c['page']}")

ask("Combien de stages d'été sont obligatoires ?")
ask("Que se passe-t-il en cas de plagiat ?")
ask("How many credits are there per semester?")