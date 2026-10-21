"""
conftest.py - Helpers dos testes de aceite da extracao.

Regras:
- `fontes/` e SOMENTE LEITURA (regra 11 do AGENTS.md). Os testes so abrem PDFs/DOCX ali.
- A extracao roda dentro de um diretorio temporario (cwd), para nao escrever em `catalogo/`
  nem no `manifest.yaml` do repositorio.
- PDF ausente -> `pytest.skip` com motivo explicito (nunca aprova em silencio).
"""

import glob
import json
import os
import sys
import tempfile
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[2]
SCRIPTS = RAIZ / "scripts" / "python"
GOLDEN = RAIZ / "tests" / "golden"

sys.path.insert(0, str(SCRIPTS))

_cache = {}


def listar_fontes(tipo):
    """Lista caminhos de fontes/: tipo 'nt' ou 'moc'."""
    sub = "notas-tecnicas" if tipo == "nt" else "moc"
    padrao = str(RAIZ / "fontes" / "*" / sub / "*")
    return sorted(p for p in glob.glob(padrao) if p.lower().endswith((".pdf", ".docx")))


def abrir_pdf(caminho):
    """Abre PDF de fontes/ para leitura; skip se o arquivo nao existir."""
    import pymupdf

    if not os.path.exists(caminho):
        pytest.skip(f"PDF de origem ausente: {caminho}")
    return pymupdf.open(caminho)


def carregar_golden(nome):
    """Le tests/golden/<nome>.json (expectativas escritas a mao)."""
    caminho = GOLDEN / f"{nome}.json"
    if not caminho.exists():
        pytest.skip(f"golden ausente: {caminho}")
    with open(caminho, encoding="utf-8") as f:
        return json.load(f)


def pdf_da_nt(nome_base):
    """Caminho do PDF de uma NT pelo nome-base (sem extensao); skip se ausente."""
    achados = glob.glob(str(RAIZ / "fontes" / "*" / "notas-tecnicas" / f"{nome_base}.pdf"))
    if not achados:
        pytest.skip(f"PDF de origem ausente para {nome_base}")
    return achados[0]


def _fechar_loggers():
    """Fecha FileHandlers dos loggers do extrator (no Windows travam o diretorio temporario)."""
    import logging

    for nome, lg in list(logging.Logger.manager.loggerDict.items()):
        if nome.startswith("extrair_nt_") and isinstance(lg, logging.Logger):
            for h in list(lg.handlers):
                h.close()
                lg.removeHandler(h)


def extrair(caminho, tipo="nt"):
    """
    Extrai um PDF/DOCX para dict, sem efeitos colaterais no repositorio
    (cwd temporario; manifest inexistente). Resultado em cache por sessao.
    """
    caminho = os.path.abspath(caminho)  # antes do chdir para o diretorio temporario
    chave = (tipo, caminho)
    if chave in _cache:
        return _cache[chave]

    if not os.path.exists(caminho):
        pytest.skip(f"arquivo de origem ausente: {caminho}")

    if tipo == "nt":
        from extrair_nt import extrair_nt as func
    else:
        from extrair_moc import extrair_moc as func

    cwd = os.getcwd()
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        os.chdir(tmp)
        try:
            resultado = func(os.path.abspath(caminho), os.path.join(tmp, "manifest-inexistente.yaml"))
        finally:
            os.chdir(cwd)
            _fechar_loggers()
    _cache[chave] = resultado
    return resultado


def snapshot_dir(diretorio):
    """{caminho relativo: sha256} de todos os arquivos de um diretorio (para detectar alteracoes)."""
    import hashlib

    base = Path(diretorio)
    resultado = {}
    if not base.exists():
        return resultado
    for p in sorted(base.rglob("*")):
        if p.is_file():
            h = hashlib.sha256()
            with open(p, "rb") as f:
                for bloco in iter(lambda: f.read(1 << 20), b""):
                    h.update(bloco)
            resultado[p.relative_to(base).as_posix()] = h.hexdigest()
    return resultado


def diferencas_snapshot(antes, depois):
    """Retorna (criados, removidos, alterados) entre dois snapshots."""
    criados = sorted(set(depois) - set(antes))
    removidos = sorted(set(antes) - set(depois))
    alterados = sorted(k for k in set(antes) & set(depois) if antes[k] != depois[k])
    return criados, removidos, alterados


@pytest.fixture(scope="session", autouse=True)
def fontes_somente_leitura():
    """Garante a regra 11: a suite nao cria, altera nem apaga nada em fontes/."""
    antes = snapshot_dir(RAIZ / "fontes")
    yield
    depois = snapshot_dir(RAIZ / "fontes")
    criados, removidos, alterados = diferencas_snapshot(antes, depois)
    assert not (criados or removidos or alterados), (
        f"fontes/ foi modificada pelos testes: criados={criados} removidos={removidos} alterados={alterados}"
    )


@pytest.fixture(scope="session")
def raiz():
    return RAIZ
