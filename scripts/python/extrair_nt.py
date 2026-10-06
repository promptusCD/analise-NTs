#!/usr/bin/env python3
"""
extrair_nt.py - Extrai informacoes de NTs fiscais com marcações de cor.

Uso:
    python extrair_nt.py <arquivo.pdf> [--output json|md|both] [--manifest <path>]

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
    parse_sections,
    parse_items_from_section,
    calculate_sha256,
)
from utils.saida import gerar_json_nt, gerar_md_nt, salvar_saida
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


def extrair_nt(pdf_path, output_format="both", manifest_path=None):
    """
    Orquestra extracao completa de uma NT.

    Args:
        pdf_path: caminho para o PDF
        output_format: "json", "md" ou "both"
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

    doc.close()

    # Parsear metadados
    metadata = parse_nt_metadata(page_texts, filename)
    logger.info(f"Metadados: NT={metadata['nt']}, v={metadata['versao']}, doc={metadata['documento']}")

    # Parsear cronograma
    cronograma = parse_cronograma(page_texts)
    logger.info(f"Cronograma: {len(cronograma)} blocos encontrados")

    # Parsear secoes do texto completo
    sections = parse_sections(page_texts)
    logger.info(f"Secoes: {len(sections)} encontradas")

    # Usar linhas agregadas diretamente como itens
    # Filtrar linhas vazias ou muito curtas
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
        if text in ("•", "", ">", ">>", "-"):
            continue
        # Ignorar sumario (linhas com muitos pontos)
        if re.match(r'^[\w\s]+\.{20,}\d+$', text):
            continue
        itens_filtrados.append(item)

    # Associar itens a secoes com base no conteudo
    itens_com_secao = []
    secao_atual = "0"
    secao_titulo_atual = "Geral"

    # Padroes de secao para NTs fiscais
    # "1 Resumo", "2 Regras solicitadas...", "3 Alteração no leiaute..."
    secao_patterns = [
        re.compile(r'^(\d{1,2})\s+([A-Z][\w\s]{3,80})$'),  # "1 Resumo"
        re.compile(r'^(\d{1,2})\s+([A-Z][\w\s]{3,80})\s*$'),  # "1 Resumo "
    ]

    for item in itens_filtrados:
        text = item.get("text", "").strip()

        # Detectar secoes
        secao_encontrada = False
        for pattern in secao_patterns:
            m = pattern.match(text)
            if m:
                num = m.group(1)
                titulo = m.group(2).strip()
                # So aceitar secoes com titulos significativos
                if not titulo.isdigit() and len(titulo) > 3:
                    secao_atual = num
                    secao_titulo_atual = titulo
                    secao_encontrada = True
                    break

        if secao_encontrada:
            continue

        item["secao"] = secao_atual
        item["secao_titulo"] = secao_titulo_atual
        item["id"] = ""
        item["tipo"] = "item"
        itens_com_secao.append(item)

    # Se nao encontrou itens, usar todos os itens filtrados
    if not itens_com_secao and itens_filtrados:
        logger.warning("Nenhuma secao encontrada, usando todos os itens como lista plana")
        for i, item in enumerate(itens_filtrados):
            item["secao"] = "0"
            item["secao_titulo"] = "Geral"
            item["id"] = str(i)
            item["tipo"] = "item"
            itens_com_secao.append(item)

    # Log de diagnostico
    stats = {}
    for item in itens_com_secao:
        m = item.get("marcacao", "SEM_MARCA")
        stats[m] = stats.get(m, 0) + 1

    logger.info(f"Estatisticas: {stats}")

    if stats.get("SEM_MARCA", 0) == len(itens_com_secao) and len(itens_com_secao) > 0:
        logger.warn("ALERTA: 100% dos itens estao SEM_MARCA - possivel falha na deteccao de cor")

    # Log de itens problematicos
    for item in itens_com_secao:
        if item.get("marcacao") == "SEM_MARCA" and any(
            kw in item.get("secao_titulo", "").lower()
            for kw in ["altera", "exclu", "modific", "inclu"]
        ):
            logger.warning(f"Item '{item.get('id', '?')}' na secao '{item.get('secao_titulo', '')}' sem marcacao (possivel regra nova inteira)")

    # Calcular SHA256
    sha256 = calculate_sha256(pdf_path)
    logger.info(f"SHA256: {sha256}")

    # Gerar JSON
    json_data = gerar_json_nt(
        metadata=metadata,
        cronograma=cronograma,
        itens=itens_com_secao,
        arquivo_origem=pdf_path,
        sha256=sha256,
    )

    # Gerar MD
    md_content = gerar_md_nt(json_data)

    # Salvar
    output_dir = os.path.join("catalogo", "nt", doc_lower)
    json_filename = f"{Path(filename).stem}.json"
    md_filename = f"{Path(filename).stem}.md"

    if output_format in ("json", "both"):
        json_path, _ = salvar_saida(json_data, md_content, output_dir, json_filename, md_filename)
        logger.info(f"JSON salvo em: {json_path}")

    if output_format in ("md", "both"):
        _, md_path = salvar_saida(json_data, md_content, output_dir, json_filename, md_filename)
        logger.info(f"MD salvo em: {md_path}")

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

    logger.info(f"Extracao concluida: {len(itens_com_secao)} itens extraidos")

    return json_data


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Extrai informacoes de NTs fiscais com marcações de cor"
    )
    parser.add_argument("arquivo", help="Caminho para o PDF da NT")
    parser.add_argument(
        "--output",
        choices=["json", "md", "both"],
        default="both",
        help="Formato de saida (default: both)",
    )
    parser.add_argument(
        "--manifest",
        default="manifest.yaml",
        help="Caminho para manifest.yaml",
    )

    args = parser.parse_args()

    if not os.path.exists(args.arquivo):
        print(f"ERRO: Arquivo nao encontrado: {args.arquivo}", file=sys.stderr)
        sys.exit(1)

    result = extrair_nt(args.arquivo, args.output, args.manifest)

    if "erro" in result:
        print(f"ERRO: {result['erro']}", file=sys.stderr)
        sys.exit(1)

    print(f"\nConcluido: {result['nt']} v{result['versao']} ({result['documento']})")
    print(f"Itens: {result['estatisticas']['total_itens']}")
    print(f"MARCACOES: {result['estatisticas']['por_marcacao']}")


if __name__ == "__main__":
    main()