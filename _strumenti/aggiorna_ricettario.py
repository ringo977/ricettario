#!/usr/bin/env python3
"""Rigenera Ricettario.html e Indice.md a partire dalle schede .md.

Uso (dal Terminale):  python3 "_strumenti/aggiorna_ricettario.py"
oppure doppio clic su "Aggiorna ricettario.command" (Mac).
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = Path(__file__).resolve().parent / "template.html"
ESCLUSI = {"LEGGIMI.md", "Indice.md"}
ORDINE = ["Antipasti e stuzzichini", "Primi piatti", "Piatti unici", "Secondi di carne",
          "Secondi di pesce", "Salse e basi", "Pane, pizza e lievitati", "Dolci", "Tecnica"]


def schede():
    for p in sorted(ROOT.rglob("*.md")):
        rel = p.relative_to(ROOT).as_posix()
        if rel.startswith("_") or p.name in ESCLUSI:
            continue
        yield rel, p.read_text(encoding="utf-8")


def meta(md):
    m = re.match(r"^﻿?---\n(.*?)\n---", md, re.S)
    out = {}
    if m:
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                out[k.strip()] = v.strip()
    return out


def main():
    docs = [{"path": rel, "md": md} for rel, md in schede()]
    data = json.dumps(docs, ensure_ascii=False).replace("</", "<\\/")
    html = TEMPLATE.read_text(encoding="utf-8").replace("/*DATA*/", data)
    (ROOT / "Ricettario.html").write_text(html, encoding="utf-8")

    # Indice.md
    righe = []
    for d in docs:
        m = meta(d["md"])
        righe.append((m.get("categoria", "Altro"), m.get("sottocategoria", ""),
                      m.get("titolo", Path(d["path"]).stem), m.get("fonte", ""), d["path"]))
    rank = lambda c: ORDINE.index(c) if c in ORDINE else 99
    righe.sort(key=lambda r: (rank(r[0]), r[1], r[2].lower()))
    out = ["# Indice del ricettario", "",
           f"{sum(1 for r in righe if r[0] != 'Tecnica')} ricette e "
           f"{sum(1 for r in righe if r[0] == 'Tecnica')} schede di tecnica. "
           "Generato automaticamente da `_strumenti/aggiorna_ricettario.py`.", ""]
    ultimo = None
    for cat, sub, tit, fonte, path in righe:
        gruppo = cat + (f" — {sub}" if sub else "")
        if gruppo != ultimo:
            out += ["", f"## {gruppo}", ""]
            ultimo = gruppo
        link = path.replace(" ", "%20").replace("(", "%28").replace(")", "%29")
        out.append(f"- [{tit}]({link})" + (f" · {fonte}" if fonte else ""))
    (ROOT / "Indice.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"Ricettario aggiornato: {len(docs)} schede.")


if __name__ == "__main__":
    main()
