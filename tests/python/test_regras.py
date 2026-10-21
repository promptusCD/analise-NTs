"""
Regras de validacao das NTs contra tests/golden/regras.json (escrito a mao a partir dos PDFs).
"""

import json

import pytest

from conftest import GOLDEN, extrair, pdf_da_nt

from verificar_extracao import regras_da_nt

pytestmark = pytest.mark.golden

_caminho = GOLDEN / "regras.json"
GOLDEN_REGRAS = (
    {k: v for k, v in json.load(open(_caminho, encoding="utf-8")).items() if not k.startswith("_")}
    if _caminho.exists()
    else {}
)

CASOS = [
    (nome, regra["id"], regra["pagina"])
    for nome, dados in sorted(GOLDEN_REGRAS.items())
    for regra in dados.get("regras", [])
]


def _regra(nome, id_, pagina):
    """Busca por (id, pagina); regra sem ID (id vazio) por (cStat, pagina), vindo do golden."""
    regras = regras_da_nt(extrair(pdf_da_nt(nome), "nt"))
    esperado = next(r for r in GOLDEN_REGRAS[nome]["regras"] if r["id"] == id_ and r["pagina"] == pagina)
    achadas = [
        r for r in regras
        if r["id"] == id_ and r.get("pagina") == pagina and (id_ or r["cStat"] == esperado["cStat"])
    ]
    assert achadas, (
        f"{nome}: regra {id_!r} cStat {esperado['cStat']} (pag. {pagina}) nao encontrada; "
        f"na pagina: {[(r['id'], r['cStat']) for r in regras if r.get('pagina') == pagina]}"
    )
    return achadas[0]


@pytest.mark.parametrize("nome", sorted(n for n, d in GOLDEN_REGRAS.items() if "ids_completos" in d))
def test_ids_completos(nome):
    esperado = set(GOLDEN_REGRAS[nome]["ids_completos"])
    obtido = {r["id"] for r in regras_da_nt(extrair(pdf_da_nt(nome), "nt"))}
    assert obtido == esperado, f"{nome}: faltando={sorted(esperado - obtido)} sobrando={sorted(obtido - esperado)}"


@pytest.mark.parametrize("nome,id_,pagina", CASOS)
def test_cstat_da_regra(nome, id_, pagina):
    esperado = next(r for r in GOLDEN_REGRAS[nome]["regras"] if r["id"] == id_ and r["pagina"] == pagina)
    assert _regra(nome, id_, pagina)["cStat"] == esperado["cStat"]


@pytest.mark.parametrize(
    "nome,id_,pagina",
    [(n, i, p) for n, i, p in CASOS if "mensagem" in next(
        r for r in GOLDEN_REGRAS[n]["regras"] if r["id"] == i and r["pagina"] == p)],
)
def test_mensagem_completa_da_regra(nome, id_, pagina):
    esperado = next(r for r in GOLDEN_REGRAS[nome]["regras"] if r["id"] == id_ and r["pagina"] == pagina)
    assert _regra(nome, id_, pagina)["mensagem"] == esperado["mensagem"]


def test_golden_nao_vazio():
    assert CASOS, "tests/golden/regras.json ausente ou sem regras"
