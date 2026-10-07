#!/usr/bin/env python3
"""
extrair_nt.py - Extrai informacoes de NTs fiscais com marcações de cor.

Uso:
    python extrair_nt.py <arquivo.pdf> [--manifest <path>]

Dependencias:
    pip install pymupdf>=1.24.0 pyyaml
"""

import sys
import os
import re
import logging
from pathlib import Path
from datetime import datetime

# Adicionar diretorio atual ao path para imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pymupdf

from utils.cores import extract_page_content, aggregate_spans_into_lines
from utils.parsing import (
    detect_documento_from_filename,
    parse_nt_metadata,
    parse_cronograma,
    calculate_sha256,
)
from utils.classificacao import montar_secoes_typed, calcular_estatisticas
from utils.saida import gerar_json_nt, salvar_json
from utils.manifest import atualizar_status_manifest


def setup_logger(doc_name, nt_versao, log_dir):
    """Configura logger com arquivo e stdout."""
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"{nt_versao.replace('.', '_')}.log")

    logger = logging.getLogger(f"extrair_nt_{nt_versao}")
    logger.setLevel(logging.DEBUG)

    # Handler para arquivo
    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    logger.addHandler(fh)

    # Handler para stdout
    sh = logging.StreamHandler(sys.stdout)
    sh.setLevel(logging.INFO)
    sh.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
    logger.addHandler(sh)

    return logger


def extrair_nt(pdf_path, manifest_path=None):
    """
    Orquestra extracao completa de uma NT.

    Args:
        pdf_path: caminho para o PDF
        manifest_path: caminho do manifest.yaml (opcional)

    Returns:
        dict com resultado da extracao
    """
    pdf_path = os.path.abspath(pdf_path)
    filename = os.path.basename(pdf_path)

    # Detectar documento
    documento = detect_documento_from_filename(filename)

    # Configurar logger
    nt_versao = Path(filename).stem
    doc_lower = documento.lower().replace("-", "").replace("e", "")
    if doc_lower == "nf":
        doc_lower = "nfe"
    elif doc_lower == "ct":
        doc_lower = "cte"
    elif doc_lower == "mdf":
        doc_lower = "mdfe"
    log_dir = os.path.join("catalogo", "nt", doc_lower, "stdout")
    logger = setup_logger(documento, nt_versao, log_dir)

    logger.info(f"Iniciando extracao de {filename}")
    logger.info(f"Documento detectado: {documento}")

    # Abrir PDF
    try:
        doc = pymupdf.open(pdf_path)
    except Exception as e:
        logger.error(f"Erro ao abrir PDF: {e}")
        return {"erro": str(e)}

    logger.info(f"PDF aberto: {len(doc)} paginas")

    # Extrair texto de todas as paginas
    page_texts = []
    all_items = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        logger.info(f"Processando pagina {page_num + 1}/{len(doc)}")

        # Extrair conteudo visual com marcacoes e agregar em linhas
        raw_items = extract_page_content(page)
        page_items = aggregate_spans_into_lines(raw_items)

        # Extrair texto puro
        text = page.get_text()
        page_texts.append(text)

        # Associar itens com pagina
        for item in page_items:
            item["pagina"] = page_num + 1
        all_items.extend(page_items)

    num_paginas = len(doc)
    doc.close()

    # Parsear metadados
    metadata = parse_nt_metadata(page_texts, filename)
    logger.info(f"Metadados: NT={metadata['nt']}, v={metadata['versao']}, doc={metadata['documento']}")

    # Parsear cronograma
    cronograma = parse_cronograma(page_texts)
    logger.info(f"Cronograma: {len(cronograma)} blocos encontrados")

    # Filtrar linhas vazias, ruido e cabecalhos repetitivos
    itens_filtrados = []
    for item in all_items:
        text = item.get("text", "").strip()
        if len(text) < 3:
            continue
        # Ignorar linhas que sao apenas numeros de pagina
        if re.match(r'^Página \d+ / \d+$', text):
            continue
        # Ignorar cabecalhos repetitivos do MDF-e
        if 'Projeto Manifesto' in text and 'Documentos Fiscais' in text:
            continue
        # Ignorar linhas "NT XXXX.XXX vX.XX"
        if re.match(r'^NT \d{4}\.\d{3} v[\d.]+$', text):
            continue
        # Ignorar linhas que sao apenas pontilhados
        if re.match(r'^[\.\-]{10,}$', text):
            continue
        # Ignorar marcadores de lista soltos
        if text in ("•", "", ">", ">>", "-"):
            continue
        # Ignorar sumario (linhas com muitos pontos)
        if re.search(r"\.{15,}\s*\d*$", text):
            continue
        itens_filtrados.append(item)

    # Ignorar cabecalhos/rodapes que se repetem em varias paginas
    paginas_por_texto = {}
    for item in itens_filtrados:
        t = item.get("text", "").strip()
        paginas_por_texto.setdefault(t, set()).add(item.get("pagina"))
    min_repeticoes = max(3, int(num_paginas * 0.4)) if num_paginas >= 3 else 3
    itens_filtrados = [
        item
        for item in itens_filtrados
        if item.get("text", "").strip().startswith("#")
        or len(paginas_por_texto.get(item.get("text", "").strip(), ())) < min_repeticoes
    ]

    # Classificar linhas em secoes tipificadas (tabela/regras/texto)
    secoes = montar_secoes_typed(itens_filtrados, logger=logger)

    # Log de diagnostico
    stats = calcular_estatisticas(secoes)
    logger.info(f"Estatisticas: {stats}")

    if stats["por_marcacao"].get("SEM_MARCA", 0) > 0:
        total = sum(stats["por_marcacao"].values())
        if stats["por_marcacao"]["SEM_MARCA"] == total and total > 0:
            logger.warn("ALERTA: 100% das unidades estao SEM_MARCA - possivel falha na deteccao de cor")

    # Calcular SHA256
    sha256 = calculate_sha256(pdf_path)
    logger.info(f"SHA256: {sha256}")

    # Gerar JSON
    json_data = gerar_json_nt(
        metadata=metadata,
        cronograma=cronograma,
        secoes=secoes,
        arquivo_origem=pdf_path,
        sha256=sha256,
    )

    # Salvar JSON
    output_dir = os.path.join("catalogo", "nt", doc_lower)
    json_filename = f"{Path(filename).stem}.json"

    json_path = salvar_json(json_data, output_dir, json_filename)
    logger.info(f"JSON salvo em: {json_path}")

    # Atualizar manifest
    if manifest_path is None:
        manifest_path = "manifest.yaml"

    if os.path.exists(manifest_path):
        rel_path = os.path.relpath(pdf_path, os.path.dirname(manifest_path) or ".")
        atualizado = atualizar_status_manifest(rel_path, "extraida", manifest_path)
        if atualizado:
            logger.info(f"Manifest atualizado: {rel_path} -> extraida")
        else:
            logger.warn(f"Nao encontrou entrada no manifest para: {rel_path}")

    logger.info(
        f"Extracao concluida: {len(secoes)} secoes, "
        f"{stats['total_regras']} regras, {stats['total_tabelas']} tabelas"
    )

    return json_data


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Extrai informacoes de NTs fiscais com marcações de cor"
    )
    parser.add_argument("arquivo", help="Caminho para o PDF da NT")
    parser.add_argument(
        "--manifest",
        default="manifest.yaml",
        help="Caminho para manifest.yaml",
    )

    args = parser.parse_args()

    if not os.path.exists(args.arquivo):
        print(f"ERRO: Arquivo nao encontrado: {args.arquivo}", file=sys.stderr)
        sys.exit(1)

    result = extrair_nt(args.arquivo, args.manifest)

    if "erro" in result:
        print(f"ERRO: {result['erro']}", file=sys.stderr)
        sys.exit(1)

    print(f"\nConcluido: {result['nt']} v{result['versao']} ({result['documento']})")
    print(f"Secoes: {len(result.get('secoes', []))}")
    print(f"Estatisticas: {result.get('estatisticas', {})}")


if __name__ == "__main__":
    main()