import os
import re
import json
from pathlib import Path
from collections import defaultdict

import fitz
import numpy as np
from sklearn.cluster import KMeans

INPUT_DIR = Path("/app/input")
OUTPUT_DIR = Path("/app/output")

def get_text_info(p):
    d = fitz.open(str(p))
    info = []
    for pg, pg_obj in enumerate(d, 1):
        blks = pg_obj.get_text("dict")["blocks"]
        for b in blks:
            if b.get("type", 0) != 0:
                continue
            for ln in b.get("lines", []):
                if not ln.get("spans"):
                    continue
                t = ""
                sz = 0
                bold = False
                fn = ""
                bb = None
                for sp in ln["spans"]:
                    part = sp["text"].strip()
                    if part:
                        t += part + " "
                        sz = max(sz, sp["size"])
                        bold = bold or (sp["flags"] & 2 != 0)
                        fn = sp.get("font", "")
                        if bb is None:
                            bb = sp["bbox"]
                t = t.strip()
                if t:
                    info.append({
                        "text": t,
                        "page": pg,
                        "font_size": round(sz, 1),
                        "is_bold": bold,
                        "font_name": fn,
                        "bbox": bb,
                        "y_position": bb[1] if bb else 0
                    })
    d.close()
    return info

def get_title(data):
    pg1 = [x for x in data if x['page'] == 1]
    if not pg1:
        return ""
    c = []
    max_sz = max(x['font_size'] for x in pg1)
    for x in pg1:
        if (x['font_size'] >= max_sz * 0.9 and
            3 <= len(x['text'].split()) <= 20 and
            x['y_position'] < 400 and
            not not_title(x['text'])):
            c.append(x)
    if c:
        c.sort(key=lambda y: (y['font_size'], -y['y_position']), reverse=True)
        return c[0]['text'].strip()
    return ""

def not_title(t):
    t = t.lower().strip()
    pats = [
        r'^\d+$', r'^page \d+', r'^www\.', r'@', r'^\(\d+\)',
        r'(january|february|march|april|may|june|july|august|september|october|november|december)',
        r'^\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4}',
    ]
    return any(re.match(p, t) for p in pats)

def get_headings(data):
    pg_sizes = {
        p: np.median([x['font_size'] for x in data if x['page'] == p])
        for p in set(x['page'] for x in data)
    }
    cand = []
    for x in data:
        med = pg_sizes[x['page']]
        if (
            (x['font_size'] > med * 1.15 or x['is_bold'] or is_num(x['text'])) and
            is_head(x['text']) and
            not looks_body(x['text'])
        ):
            cand.append(x)
    if not cand:
        return []
    szs = np.array([h['font_size'] for h in cand])
    uniq = np.unique(szs)
    if len(uniq) <= 4:
        sorted_szs = sorted(uniq, reverse=True)
        sz_lvl = {s: min(i + 1, 4) for i, s in enumerate(sorted_szs)}
    else:
        km = KMeans(n_clusters=4, random_state=42, n_init=10)
        clust = km.fit_predict(szs.reshape(-1, 1))
        ctrs = km.cluster_centers_.flatten()
        m = {c: i + 1 for i, c in enumerate(sorted(ctrs, reverse=True))}
        sz_lvl = {szs[i]: m[ctrs[clust[i]]] for i in range(len(szs))}
    res = []
    for h in cand:
        lvl = sz_lvl[h['font_size']]
        lvl = tweak_lvl(h['text'], lvl)
        res.append({
            "text": h['text'],
            "page": h['page'],
            "level": f"H{min(lvl, 4)}",
            "font_size": h['font_size'],
            "is_bold": h['is_bold']
        })
    return res

def is_num(t):
    pats = [
        r'^\d+\.\s+[A-Z]', r'^\d+\.\d+\s+[A-Z]',
        r'^(Chapter|Section|Appendix)\s+[A-Z0-9]'
    ]
    return any(re.match(p, t, re.IGNORECASE) for p in pats)

def is_head(t):
    t = t.strip()
    if len(t.split()) > 15 or len(t) < 3:
        return False
    if not any(c.isalpha() for c in t):
        return False
    if re.search(r'(.)\1{3,}', t) or t.count('.') > 4 or t.count(',') > 3:
        return False
    if t.endswith((',', ';', ':')) or (t.endswith('.') and not re.match(r'^\d+\.', t)):
        return False
    return True

def looks_body(t):
    t = t.strip().lower()
    return any([
        len(t.split()) > 15,
        t.endswith(('.', ',', ';', ')', ']')),
        re.search(r'\b(the|and|or|however|therefore|moreover|additionally)\b', t),
        len(t) > 100,
        re.search(r'\d{4}[-/]\d{2}[-/]\d{2}', t),
    ])

def tweak_lvl(t, lvl):
    t = t.strip().lower()
    hi = ['table of contents', 'references', 'introduction', 'conclusion',
          'appendix', 'acknowledgements', 'abstract', 'summary', 'overview']
    if any(w in t for w in hi):
        return 1
    if re.match(r'^\d+\.\s+', t): return 1
    elif re.match(r'^\d+\.\d+\s+', t): return 2
    elif re.match(r'^\d+\.\d+\.\d+\s+', t): return 3
    return lvl

def get_outline(p):
    try:
        info = get_text_info(p)
        if not info:
            return "", []
        ttl = get_title(info)
        h = get_headings(info)
        seen = set()
        out = []
        for x in h:
            if x['text'].strip().lower() == ttl.strip().lower():
                continue
            k = (x['level'], x['text'].strip())
            if k not in seen:
                seen.add(k)
                out.append({
                    "level": x['level'],
                    "text": x['text'],
                    "page": x['page']
                })
        out.sort(key=lambda x: x['page'])
        return ttl, out
    except:
        return "", []

def run_all():
    pdfs = list(INPUT_DIR.glob("*.pdf"))
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for p in pdfs:
        ttl, o = get_outline(p)
        res = {"title": ttl, "outline": o}
        with open(OUTPUT_DIR / f"{p.stem}.json", "w", encoding="utf-8") as f:
            json.dump(res, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    run_all()
