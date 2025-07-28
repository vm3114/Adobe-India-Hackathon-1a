# Challenge 1A

Basic setup to extract outline structure + guessed title from PDF files. Outputs a JSON file per PDF.

##  Approach

This solution uses a rule-based layout analysis pipeline to infer the logical structure of a PDF document. It does **not** rely on LLMs or cloud APIs, and is suitable for offline use.

Steps:
1. **Parse PDF using PyMuPDF (`fitz`)** to extract lines with font size, position, and boldness.
2. **Guess the title** by identifying the most prominent top-level text on page 1.
3. **Infer headings**:
   - Uses boldness, font size (compared to median page size), and position.
   - Clusters font sizes to assign levels (H1–H4).
   - Rejects headings with body-like patterns or noisy formatting.

---


## Models & Libraries Used

This is a lightweight, zero-ML solution. Main dependencies:
- [`PyMuPDF`](https://pymupdf.readthedocs.io/) – for parsing PDF layout data
- `scikit-learn` – for clustering font sizes (KMeans)
- `numpy` – utility
- `json`, `re`, `pathlib` – standard Python libraries

---

## How to Use

Just build it:
```
docker build --platform linux/amd64 -t challenge1a:mogus .
```

Then run it (Make folder `input/` with PDFs in the current directory):
```
docker run --rm -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output --network none challenge1a:mogus
```
---
## Output

Each PDF gets a `.json` file in `output/` with:
- `"title"`: best guess at document title (if found)
- `"outline"`: list of heading-ish things, kind of sorted
