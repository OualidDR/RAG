from dotenv import load_dotenv
from groq import Groq
from search import search

load_dotenv()
client = Groq()
MODEL = "openai/gpt-oss-20b"

SYSTEM = (
    "Tu es l'assistant des élèves de l'ENSIAS. "
    "Réponds UNIQUEMENT à partir du contexte fourni. "
    "Si la réponse n'est pas dans le contexte, dis que tu ne sais pas "
    "et conseille de contacter l'administration. "
    "Réponds dans la langue de la question. "
    "Cite tes sources sous la forme [1], [2]."
)

THRESHOLD = 0.35
NO_ANSWER = (
    "Je n'ai pas trouvé cette information dans les documents de l'ENSIAS. "
    "Merci de contacter l'administration. / "
    "I couldn't find this in the ENSIAS documents. Please contact the administration."
)

def build_context(hits):
    parts = []
    for i, h in enumerate(hits):
        m = h["meta"]
        title = m["article"] or m["section"] or m["chapter"]
        parts.append(f"[{i+1}] ({title}, page {m['page']})\n{h['text']}")
    return "\n\n".join(parts)

def answer(question, k=3, category=None):
    hits = search(question, k, category)
    if hits[0]["score"] < THRESHOLD:
        return NO_ANSWER, []
    
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user",
             "content": f"Contexte:\n{build_context(hits)}\n\nQuestion: {question}"},
        ],
    )
    return response.choices[0].message.content, hits

if __name__ == "__main__":
    for q in [
        "stge combien oblig",
        "Comment faire une pizza ?",
        "What is the best programming language?",
        "Quel temps fait-il à Rabat ?",
    ]:
        score = search(q, k=1)[0]["score"]
        text, hits = answer(q)
        print("\n", q)
        print(text)
        print("top score:", round(score, 2), "| sources:", len(hits))