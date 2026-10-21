"""
Marcacoes de cor (AMARELO/VERDE/EXCLUIDO) das paginas de referencia contra tests/golden/marcacoes.json.
"""

import json

import pytest

from conftest import GOLDEN, extrair, pdf_da_nt

from verificar_extracao import regras_da_nt

pytestmark = pytest.mark.golden

_caminho = GOLDEN / "marcacoes.json"
GOLDEN_MARCACOES = (
    {k: v for k, v in json.load(open(_caminho, encoding="utf-8")).items() if not k.startswith("_")}
    if _caminho.exists()
    else {}
)

CASOS = [(nome, i) for nome, itens in sorted(GOLDEN_MARCACOES.items()) for i in range(len(itens))]


def _achar_regra(dados, ref):
    achadas = [
        r
        for r in regras_da_nt(dados)
        if r["id"] == ref["id"]
        and r.get("pagina") == ref["pagina"]
        and (not ref.get("cStat") or r["cStat"] == ref["cStat"])
    ]
    assert achadas, f"regra {ref} nao encontrada"
    return achadas[0]


def _linhas_de_tabela(dados):
    return [ln for s in dados["secoes"] if s["tipo"] == "tabela" for ln in s["linhas"]]


@pytest.mark.parametrize("nome,i", CASOS, ids=[f"{n}[{i}]" for n, i in CASOS])
def test_marcacao_da_pagina_de_referencia(nome, i):
    esperado = GOLDEN_MARCACOES[nome][i]
    dados = extrair(pdf_da_nt(nome), "nt")

    if esperado["tipo"] == "regra":
        assert _achar_regra(dados, esperado)["marcacao"] == esperado["marcacao"]

    elif esperado["tipo"] == "nota":
        regra = _achar_regra(dados, esperado["regra"])
        notas = [n for n in regra["notas"] if n["texto"].startswith(esperado["comeca_com"])]
        assert notas, f"nota {esperado['comeca_com']!r} nao encontrada; notas: {[n['texto'][:40] for n in regra['notas']]}"
        assert notas[0]["marcacao"] == esperado["marcacao"], notas[0]

    else:  # linha de tabela de leiaute
        linhas = [
            ln for ln in _linhas_de_tabela(dados)
            if ln.get("pagina") == esperado["pagina"] and ln["texto"].startswith(esperado["comeca_com"])
        ]
        assert linhas, f"linha {esperado['comeca_com']!r} (pag. {esperado['pagina']}) nao encontrada"
        assert linhas[0]["marcacao"] == esperado["marcacao"], linhas[0]
        if "trecho" in esperado:
            t = esperado["trecho"]
            assert any(
                x["marcacao"] == t["marcacao"] and t["contem"] in x["texto"] for x in linhas[0].get("trechos", [])
            ), f"trecho {t} ausente em {linhas[0].get('trechos')}"


def test_golden_nao_vazio():
    assert CASOS
