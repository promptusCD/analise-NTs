"""
utils/manifest.py - Gerenciamento do manifest.yaml.

Leitura, escrita e atualizacao de status de ingestao.
"""

import yaml
import hashlib
from pathlib import Path


DEFAULT_MANIFEST_PATH = "manifest.yaml"


def ler_manifest(manifest_path=None):
    """
    Le manifest.yaml e retorna lista de entradas.

    Returns:
        list de dicts
    """
    if manifest_path is None:
        manifest_path = DEFAULT_MANIFEST_PATH

    with open(manifest_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if data is None:
        return []

    return data


def salvar_manifest(entradas, manifest_path=None):
    """
    Salva lista de entradas no manifest.yaml.

    Args:
        entradas: list de dicts
        manifest_path: caminho do arquivo
    """
    if manifest_path is None:
        manifest_path = DEFAULT_MANIFEST_PATH

    with open(manifest_path, "w", encoding="utf-8") as f:
        yaml.dump(entradas, f, default_flow_style=False, allow_unicode=True, sort_keys=False)


def atualizar_status_manifest(arquivo, novo_status, manifest_path=None):
    """
    Atualiza status_ingestao de uma entrada especifica.

    Args:
        arquivo: caminho do arquivo (campo 'arquivo' do manifest)
        novo_status: novo valor para status_ingestao
        manifest_path: caminho do manifest

    Returns:
        bool: True se atualizou, False se nao encontrou
    """
    entradas = ler_manifest(manifest_path)
    atualizado = False

    # Normalizar separadores: manifest usa '/', Windows gera '\' em os.path.relpath
    arquivo_norm = arquivo.replace("\\", "/")

    for entrada in entradas:
        if entrada.get("arquivo", "").replace("\\", "/") == arquivo_norm:
            entrada["status_ingestao"] = novo_status
            atualizado = True
            break

    if atualizado:
        salvar_manifest(entradas, manifest_path)

    return atualizado


def adicionar_manifest_moc(moc_data, manifest_path=None):
    """
    Adiciona entrada para MOC nao registrado no manifest.

    Args:
        moc_data: dict com documento, versao, secao, arquivo_origem, sha256
        manifest_path: caminho do manifest

    Returns:
        bool: True se adicionou, False se ja existe
    """
    entradas = ler_manifest(manifest_path)

    # Normalizar separadores: manifest usa '/', Windows gera '\' em os.path.relpath
    novo_arquivo = moc_data.get("arquivo_origem", "").replace("\\", "/")

    # Verificar se ja existe
    for entrada in entradas:
        if entrada.get("arquivo", "").replace("\\", "/") == novo_arquivo:
            return False

    # Criar nova entrada
    doc = moc_data.get("documento", "").lower().replace("-", "").replace("e", "")
    nova_entrada = {
        "id": f"{doc.upper()}-MOC-{moc_data.get('versao', '')}",
        "documento": moc_data.get("documento", ""),
        "tipo": "moc",
        "versao": moc_data.get("versao", ""),
        "titulo": f"MOC {moc_data.get('secao', '')}",
        "arquivo": novo_arquivo,
        "sha256": moc_data.get("sha256", ""),
        "status_ingestao": "extraida",
        "confianca": "oficial",
    }

    entradas.append(nova_entrada)
    salvar_manifest(entradas, manifest_path)
    return True


def listar_manifest(manifest_path=None):
    """
    Lista status de todas as entradas do manifest.

    Returns:
        list de dicts com resumo
    """
    entradas = ler_manifest(manifest_path)
    resumo = []

    for entrada in entradas:
        resumo.append({
            "id": entrada.get("id", ""),
            "documento": entrada.get("documento", ""),
            "tipo": entrada.get("tipo", "nota_tecnica"),
            "nt": entrada.get("nt", ""),
            "versao": entrada.get("versao", ""),
            "status": entrada.get("status_ingestao", "pendente"),
        })

    return resumo