from store import model, collection

def search(question, k=3, category=None):
    q = model.encode([question], normalize_embeddings=True)
    res = collection.query(
        query_embeddings=q.tolist(),
        n_results=k,
        where={"category": category} if category else None,
    )
    hits = []
    for text, meta, dist in zip(res["documents"][0],
                                res["metadatas"][0],
                                res["distances"][0]):
        hits.append({"text": text, "meta": meta, "score": 1 - dist})
    return hits

if __name__ == "__main__":
    questions = [
        "Combien de stages d'été sont obligatoires ?",
        "Que se passe-t-il en cas de plagiat ?",
        "How many credits are there per semester?",
    ]
    for question in questions:
        print("\n", question)
        for h in search(question):
            m = h["meta"]
            title = m["article"] or m["section"] or m["chapter"]
            print(f"  {h['score']:.2f} | {title[:55]} | page {m['page']}")