from pypdf import PdfReader
import re

r = PdfReader("raw_docs/Réglement_Etudes_Cycle_ingénieur_Validée_CE_30_Mars_2026.pdf")

CH3 = "CHAPITRE III : UTILISATION DES SERVICES ET DES DISPOSITIFS INFORMATIQUES ET DE TÉLÉCOMMUNICATION"

def article_number(title):
    m = re.match(r"Article\s+(\d+)", title)
    return int(m.group(1)) if m else None

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

HEADER = re.compile(r"^Règlement des études\s*[–-]\s*ENSIAS\s*_*\s*\d+\s*$")

def clean_page(text):
    kept = []
    for line in text.split("\n"):
        if HEADER.match(line.strip()):
            continue
        kept.append(line.rstrip())
    return "\n".join(kept)

raw = r.pages[4].extract_text()


removed = 0
for p in r.pages:
    for line in p.extract_text().split("\n"):
        if HEADER.match(line.strip()):
            removed += 1
print("\nheader lines removed:", removed)

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

lines = load_pdf_lines("raw_docs/Réglement_Etudes_Cycle_ingénieur_Validée_CE_30_Mars_2026.pdf")


CHAPTER = re.compile(r"^CHAPITRE\s+[IVX]+\s*:")
SECTION = re.compile(r"^[IVX]+\.\d+\.\s+\S")
ARTICLE = re.compile(r"^Article\s+\d+")
INTRO = re.compile(
    r"^(PRÉAMBULE|L[’']INGÉNIEUR|CARACTERISTIQUES DE LA FORMATION D[’']INGÉNIEUR)\s*$"
)

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

chunks = build_chunks(lines, "Réglement_Etudes_Cycle_ingénieur_Validée_CE_30_Mars_2026.pdf")

chunks = fix_chunks(build_chunks(lines, "Réglement_Etudes_Cycle_ingénieur_Validée_CE_30_Mars_2026.pdf"))
print("\n=== NEW TEST ===")
print("chunks:", len(chunks))
for c in chunks:
    if not c["article"]:
        print("page", c["page"], "|", len(c["text"]), "chars |",
              (c["section"] or c["chapter"] or "(cover)")[:45])

