"""
Cronograma das NTs contra tests/golden/cronograma.json (escrito a mao a partir da
tabela 'Historico de Alteracoes / Cronograma' de cada PDF).
"""

import json
import os
import re

import pytest

from conftest import GOLDEN, extrair, pdf_da_nt

pytestmark = pytest.mark.golden

_caminho = GOLDEN / "cronograma.json"
GOLDEN_CRONOGRAMA = (
    {k: v for k, v in json.load(open(_caminho, encoding="utf-8")).items() if not k.startswith("_")}
    if _caminho.exists()
    else {}
)


def _norm(texto):
    return re.sub(r"\s+", " ", texto or "").strip().lower()


def _tripla(entrada):
    return (entrada["versao"], entrada["homologacao"], entrada["producao"])


@pytest.mark.parametrize("nome", sorted(GOLDEN_CRONOGRAMA))
def test_cronograma_igual_ao_pdf(nome):
    esperado = GOLDEN_CRONOGRAMA[nome]["linhas"]
    dados = extrair(pdf_da_nt(nome), "nt")
    obtido = dados["cronograma"]

    assert [_tripla(e) for e in obtido] == [_tripla(e) for e in esperado], (
        f"{nome}: cronograma diferente do PDF (pag. {GOLDEN_CRONOGRAMA[nome]['pagina']})"
    )


@pytest.mark.parametrize("nome", sorted(GOLDEN_CRONOGRAMA))
def test_cronograma_descricao_da_linha_correta(nome):
    esperado = GOLDEN_CRONOGRAMA[nome]["linhas"]
    obtido = extrair(pdf_da_nt(nome), "nt")["cronograma"]
    if len(obtido) != len(esperado):
        pytest.fail(f"{nome}: {len(obtido)} entradas, esperado {len(esperado)}")
    for i, (o, e) in enumerate(zip(obtido, esperado)):
        assert _norm(e["descricao_contem"]) in _norm(o.get("descricao", "")), (
            f"{nome}[{i}] v{e['versao']}: descricao nao contem {e['descricao_contem']!r}; obtido {o.get('descricao')!r}"
        )


def test_golden_cobre_todas_as_nts_do_acervo():
    from conftest import listar_fontes

    nomes = {os.path.splitext(os.path.basename(p))[0] for p in listar_fontes("nt")}
    assert nomes <= set(GOLDEN_CRONOGRAMA), f"NTs sem golden de cronograma: {sorted(nomes - set(GOLDEN_CRONOGRAMA))}"


def test_sem_tabela_reconhecida_devolve_lista_vazia_e_avisa(caplog):
    """Texto sem tabela de controle de versoes: [] + aviso ERRO_DATA_NAO_ENCONTRADA (nada inventado)."""
    import logging

    from utils.parsing import parse_cronograma

    with caplog.at_level(logging.WARNING):
        resultado = parse_cronograma(["Pagina sem tabela de cronograma", "Outra pagina qualquer"])
    assert resultado == []
    assert any("ERRO_DATA_NAO_ENCONTRADA" in r.getMessage() for r in caplog.records)
