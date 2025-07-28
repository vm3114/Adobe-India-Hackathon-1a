import json
import re
from pathlib import Path
from llmsherpa.readers import LayoutPDFReader

INPUT_DIR = Path("/app/input")
OUTPUT_DIR = Path("/app/output")

def heading_level(level: int) -> str:
    return f"H{min(level, 4)}"

def is_clean_heading(text: str) -> bool:
    text = text.strip()
    if len(text.split()) > 10 or text.endswith(('.', ':')) or not any(c.isalpha() for c in text):
        return False
    if not (text.isupper() or text.istitle()):
        return False
    if re.search(r"(.)\1{3,}", text):
        return False
    return True

def extract_outline(doc):
    outline = []
    for section in doc.sections():
        text = section.title.strip()
        if is_clean_heading(text):
            outline.append({
                "level": heading_level(section.level),
                "text": text,
                "page": section.page_idx
            })
    return outline

def process_all_pdfs():
    reader = LayoutPDFReader("http://localhost:5001/api/parseDocument")
    pdf_files = list(INPUT_DIR.glob("*.pdf"))
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for pdf_path in pdf_files:
        try:
            doc = reader.read_pdf(str(pdf_path))
            outline = extract_outline(doc)
            title = outline[0]["text"] if outline else ""
            output = {"title": title, "outline": outline}
            with open(OUTPUT_DIR / f"{pdf_path.stem}.json", "w", encoding="utf-8") as f:
                json.dump(output, f, indent=2, ensure_ascii=False)
            print(f"[✓] Processed: {pdf_path.name}")
        except Exception as e:
            print(f"[✗] Failed: {pdf_path.name} – {e}")

if __name__ == "__main__":
    process_all_pdfs()
