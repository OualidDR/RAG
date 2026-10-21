from pypdf import PdfReader
import re
import os



def article_number(title):
    m = re.match(r"Article\s+(\d+)", title)
    return int(m.group(1)) if m else None




def clean_page(text):
    kept = []
    for line in text.split("\n"):
        if HEADER.match(line.strip()):
            continue
        kept.append(line.rstrip())
    return "\n".join(kept)



def load_pdf_lines(path):
    lines = []
    for n, page in enumerate(PdfReader(path).pages, start=1):
        text = page.extract_text()
        if "SOMMAIRE" in text:
            continue
        for line in clean_page(text).split("\n"):
            if line.strip():
                lines.append((n, line.strip()))
    return lines


HEADER = re.compile(r"^Règlement des études\s*[–-]\s*ENSIAS\s*_*\s*\d+\s*$")
CHAPTER = re.compile(r"^CHAPITRE\s+[IVX]+\s*:")
SECTION = re.compile(r"^[IVX1]+\.\d+\.\s+\S")
ARTICLE = re.compile(r"^Article\s+\d+")
INTRO = re.compile(
    r"^(PRÉAMBULE|L[’']INGÉNIEUR|CARACTERISTIQUES DE LA FORMATION D[’']INGÉNIEUR)\s*$"
)


def process_pdf(path):
    lines = load_pdf_lines(path)
    chunks = build_chunks(lines, os.path.basename(path))
    chunks = fix_chunks(chunks)
    for c in chunks:
        if c["article"]:
            new = clean_title(c["article"])
            c["text"] = c["text"].replace(c["article"], new, 1)
            c["article"] = new
    return chunks


def build_chunks(lines, source):
    chunks = []
    chapter, section = "", ""
    current = {"source": source, "chapter": "", "section": "",
               "article": "", "page": 1, "lines": []}

    for page, line in lines:
        if CHAPTER.match(line):
            kind = "chapter"
        elif SECTION.match(line):
            kind = "section"
        elif ARTICLE.match(line):
            kind = "article"
        elif INTRO.match(line):
            kind = "intro"
        else:
            current["lines"].append(line)
            continue

        if current["lines"]:
            chunks.append(current)

        if kind == "chapter":
            chapter, section = line, ""
        elif kind == "section":
            section = line
        elif kind == "intro":
            section = line

        current = {"source": source, "chapter": chapter, "section": section,
                   "article": line if kind == "article" else "",
                   "page": page,
                   "lines": [line] if kind in ("article", "intro") else []}

    if current["lines"]:
        chunks.append(current)

    for c in chunks:
        c["text"] = "\n".join(c.pop("lines"))
    return chunks

CH3 = "CHAPITRE III : UTILISATION DES SERVICES ET DES DISPOSITIFS INFORMATIQUES ET DE TÉLÉCOMMUNICATION"

def fix_chunks(chunks):
    fixed = []
    for c in chunks:
        if not c["article"] and not c["section"] and len(c["text"]) < 80:
            continue
        n = article_number(c["article"])
        if n is not None and 52 <= n <= 61:
            c["chapter"] = CH3
            c["section"] = ""
        fixed.append(c)
    return fixed

CODE = re.compile(r"\s*\(CNPN[^)]*\)+\s*")

def clean_title(title):
    return CODE.sub(" ", title).strip()

def save_for_review(chunks, folder="processed"):
    os.makedirs(folder, exist_ok=True)
    name = os.path.splitext(chunks[0]["source"])[0] + ".md"
    out = os.path.join(folder, name)
    with open(out, "w", encoding="utf-8") as f:
        for i, c in enumerate(chunks):
            title = c["article"] or c["section"] or c["chapter"] or "(cover)"
            f.write(f"## [{i}] {title}\n")
            f.write(f"page: {c['page']} | chapter: {c['chapter']} | section: {c['section']}\n\n")
            f.write(c["text"] + "\n\n---\n\n")
    return out


if __name__ == "__main__":
    chunks = process_pdf("raw_docs/Réglement_Etudes_Cycle_ingénieur_Validée_CE_30_Mars_2026.pdf")
    out = save_for_review(chunks)
    print("chunks:", len(chunks), "->", out)
    print("titles still containing CNPN:", sum("CNPN" in c["article"] for c in chunks))
    for c in chunks:
        if c["article"].startswith("Article 30"):
            print("Article 30 section:", c["section"])