from pathlib import Path

def load_documents(folder) :
    docs = []
    for path in Path(folder).glob("*.md") :
        text = path.read_text(encoding= "utf-8")
        docs.append((path.name, text))
    return docs

if __name__ == "__main__":
    docs = load_documents("docs")
    for name, text in docs :
        print(name, "->", len(text), "characters")























































