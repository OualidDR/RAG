from search import search

in_domain = [
    "Combien de stages d'été sont obligatoires ?",
    "Que se passe-t-il en cas de plagiat ?",
    "How many credits are there per semester?",
    "Combien de PFE un élève doit-il faire ?",
    "Comment fonctionne le rattrapage ?",
    "Que risque un élève absent à un examen ?",
]
out_domain = [
    "Quelle est la capitale de la France ?",
    "Quel temps fait-il à Rabat ?",
    "Comment faire une pizza ?",
    "Qui a gagné la dernière coupe du monde ?",
    "What is the best programming language?",
]

def show(title, questions):
    print("\n", title)
    for q in questions:
        score = search(q, k=1)[0]["score"]
        print(f"  {score:.2f} | {q}")

show("DANS LE DOMAINE", in_domain)
show("HORS DOMAINE", out_domain)