#!/usr/bin/env python3
"""
gerar_fixtures_spans.py - Serializa os spans de paginas especificas de PDFs de fontes/
para tests/fixtures/ (somente leitura em fontes/).

As fixtures permitem testar utils/colunas.py sem abrir o PDF.

Uso:
    python gerar_fixtures_spans.py
"""

import json
import os
import sys
import warnings

warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pymupdf

from utils.cores import extract_page_content

RAIZ = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

# (nome da fixture, pdf relativo a raiz, pagina 1-based)
PAGINAS = [
    ("nt2026007_p6", "fontes/nfe/notas-tecnicas/NT_2026_007_v1.10.pdf", 6),
    ("nt2026007_p9", "fontes/nfe/notas-tecnicas/NT_2026_007_v1.10.pdf", 9),
    ("nt2026008_p7", "fontes/nfe/notas-tecnicas/NT_2026_008_v1.00_Valor_Liquido.pdf", 7),
    ("cte2026004_p8", "fontes/cte/notas-tecnicas/CTe_NT_2026_004_v1.00.pdf", 8),
    ("cte2026004_p9", "fontes/cte/notas-tecnicas/CTe_NT_2026_004_v1.00.pdf", 9),
]

CAMPOS = ("text", "bbox", "size", "marcacao", "bold", "strikethrough", "text_color")


def main():
    saida = os.path.join(RAIZ, "tests", "fixtures")
    os.makedirs(saida, exist_ok=True)
    for nome, pdf, pagina in PAGINAS:
        doc = pymupdf.open(os.path.join(RAIZ, pdf))
        itens = extract_page_content(doc[pagina - 1])
        enxutos = [{k: i[k] for k in CAMPOS if k in i} for i in itens]
        caminho = os.path.join(saida, f"spans_{nome}.json")
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump({"pdf": pdf, "pagina": pagina, "largura": doc[pagina - 1].rect.width, "spans": enxutos},
                      f, ensure_ascii=False, indent=1)
        print(f"{nome}: {len(enxutos)} spans -> {os.path.relpath(caminho, RAIZ)}")
        doc.close()


if __name__ == "__main__":
    main()
