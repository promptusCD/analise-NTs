"""
utils/saida.py - Geracao de JSON para NTs e MOCs.

O MD nao e gerado por Python: a IA le o JSON e produz o MD
(command /gerar-md e /fiscal-processar).
"""

import json
import os
from datetime import datetime, timezone

from utils.classificacao import calcular_estatisticas


def gerar_json_nt(metadata, cronograma, secoes, arquivo_origem, sha256):
    """
    Gera JSON robusto para NT com secoes tipificadas.

    Args:
        metadata: dict com nt, versao, documento, titulo
        cronograma: lista de dicts com versao, homologacao, producao (literais)
        secoes: lista de secoes tipificadas (ver utils/classificacao.py)
        arquivo_origem: caminho do arquivo original
        sha256: hash SHA256 do arquivo

    Returns:
        dict no formato JSON
    """
    return {
        "nt": metadata.get("nt", ""),
        "versao": metadata.get("versao", ""),
        "documento": metadata.get("documento", ""),
        "titulo": metadata.get("titulo", ""),
        "arquivo_origem": str(arquivo_origem),
        "sha256": sha256,
        "extraido_em": datetime.now(timezone.utc).isoformat(),
        "tipo_documento": "NT",
        "cronograma": cronograma,
        "secoes": secoes,
        "estatisticas": calcular_estatisticas(secoes),
    }


def gerar_json_moc(metadata, secoes, regras_validacao, campos_leiaute, arquivo_origem, sha256):
    """
    Gera JSON robusto para MOC.

    Args:
        metadata: dict com documento, versao, secao, titulo
        secoes: lista hierarquica {numero, titulo, subsecoes[]}
        regras_validacao: lista {id, cStat, descricao, modelo, aplicacao}
        campos_leiaute: lista {tag, tipo, ocorrencia, descricao}
        arquivo_origem: caminho do arquivo original
        sha256: hash SHA256 do arquivo

    Returns:
        dict no formato JSON
    """
    return {
        "documento": metadata.get("documento", ""),
        "versao": metadata.get("versao", ""),
        "secao": metadata.get("secao", ""),
        "titulo": metadata.get("titulo", ""),
        "arquivo_origem": str(arquivo_origem),
        "sha256": sha256,
        "extraido_em": datetime.now(timezone.utc).isoformat(),
        "tipo_documento": "MOC",
        "secoes": secoes,
        "regras_validacao": regras_validacao,
        "campos_leiaute": campos_leiaute,
    }


def salvar_json(json_data, output_dir, json_filename):
    """
    Salva JSON no diretorio de saida.

    Args:
        json_data: dict do JSON
        output_dir: diretorio base (ex: catalogo/nt/nfe/)
        json_filename: nome do arquivo JSON

    Returns:
        caminho do arquivo salvo
    """
    os.makedirs(output_dir, exist_ok=True)
    json_path = os.path.join(output_dir, json_filename)

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)

    return json_path
