#!/usr/bin/env python3
"""
extrair_moc.py - Extrai informacoes de MOCs (PDF e DOCX).

Uso:
    python extrair_moc.py <arquivo.pdf|docx> [--manifest <path>]

Dependencias:
    pip install pymupdf>=1.24.0 pyyaml python-docx>=1.1.0
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pymupdf

from utils.parsing import (
    detect_documento_from_filename,
    detect_is_moc,
    parse_moc_metadata,
    parse_moc_sections,
    parse_moc_regras,
    parse_moc_campos,
    calculate_sha256,
)
from utils.saida import gerar_json_moc, gerar_md_moc, salvar_saida
from utils.manifest import adicionar_manifest_moc


def extrair_moc_pdf(pdf_path):
    """Extrai conteudo de um MOC em PDF."""
    doc = pymupdf.open(pdf_path)
    page_texts = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()
        page_texts.append(text)

    doc.close()
    return page_texts


def extrair_moc_docx(docx_path):
    """Extrai conteudo de um MOC em DOCX."""
    try:
        import docx
        doc = docx.Document(docx_path)
        page_texts = []
        current_page = []

        for para in doc.paragraphs:
            current_page.append(para.text)
            # Simular quebra de pagina a cada 50 paragrafos
            if len(current_page) >= 50:
                page_texts.append("\n".join(current_page))
                current_page = []

        if current_page:
            page_texts.append("\n".join(current_page))

        return page_texts
    except ImportError:
        print("ERRO: python-docx nao instalado. Execute: pip install python-docx", file=sys.stderr)
        return []


def extrair_moc(file_path, manifest_path=None):
    """
    Orquestra extracao completa de um MOC.

    Args:
        file_path: caminho para o arquivo (PDF ou DOCX)
        manifest_path: caminho do manifest.yaml (opcional)

    Returns:
        dict com resultado da extracao
    """
    file_path = os.path.abspath(file_path)
    filename = os.path.basename(file_path)
    ext = Path(filename).suffix.lower()

    print(f"Processando MOC: {filename}")

    # Extrair texto
    if ext == ".docx":
        page_texts = extrair_moc_docx(file_path)
    else:
        page_texts = extrair_moc_pdf(file_path)

    if not page_texts:
        return {"erro": "Nao foi possivel extrair conteudo do arquivo"}

    # Parsear metadados
    metadata = parse_moc_metadata(page_texts, filename)
    print(f"Documento: {metadata['documento']}, Versao: {metadata['versao']}")

    # Extrair secoes, regras e campos
    secoes = parse_moc_sections(page_texts)
    regras = parse_moc_regras(page_texts)
    campos = parse_moc_campos(page_texts)

    print(f"Secoes: {len(secoes)}, Regras: {len(regras)}, Campos: {len(campos)}")

    # Calcular SHA256
    sha256 = calculate_sha256(file_path)

    # Gerar JSON e MD
    json_data = gerar_json_moc(
        metadata=metadata,
        secoes=secoes,
        regras=regras,
        campos=campos,
        arquivo_origem=file_path,
        sha256=sha256,
    )

    md_content = gerar_md_moc(json_data)

    # Determinar diretorio de saida
    doc_lower = metadata["documento"].lower().replace("-", "").replace("e", "")
    if doc_lower == "nf":
        doc_lower = "nfe"
    elif doc_lower == "ct":
        doc_lower = "cte"
    elif doc_lower == "mdf":
        doc_lower = "mdfe"
    output_dir = os.path.join("catalogo", "moc", doc_lower)

    json_filename = f"{Path(filename).stem}.json"
    md_filename = f"{Path(filename).stem}.md"

    json_path, md_path = salvar_saida(json_data, md_content, output_dir, json_filename, md_filename)
    print(f"JSON: {json_path}")
    print(f"MD: {md_path}")

    # Atualizar manifest
    if manifest_path is None:
        manifest_path = "manifest.yaml"

    if os.path.exists(manifest_path):
        adicionar_manifest_moc(
            {
                "documento": metadata["documento"],
                "versao": metadata["versao"],
                "secao": metadata.get("secao", ""),
                "arquivo_origem": os.path.relpath(file_path, os.path.dirname(manifest_path) or "."),
                "sha256": sha256,
            },
            manifest_path,
        )

    return json_data


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Extrai informacoes de MOCs (PDF ou DOCX)"
    )
    parser.add_argument("arquivo", help="Caminho para o arquivo do MOC")
    parser.add_argument(
        "--manifest",
        default="manifest.yaml",
        help="Caminho para manifest.yaml",
    )

    args = parser.parse_args()

    if not os.path.exists(args.arquivo):
        print(f"ERRO: Arquivo nao encontrado: {args.arquivo}", file=sys.stderr)
        sys.exit(1)

    result = extrair_moc(args.arquivo, args.manifest)

    if "erro" in result:
        print(f"ERRO: {result['erro']}", file=sys.stderr)
        sys.exit(1)

    print(f"\nConcluido: MOC {result['documento']} v{result['versao']}")
    print(f"Secoes: {len(result.get('secoes', []))}")
    print(f"Regras: {len(result.get('regras', []))}")
    print(f"Campos: {len(result.get('campos', []))}")


if __name__ == "__main__":
    main()