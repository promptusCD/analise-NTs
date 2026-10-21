"""
Metadados das NTs (nt, documento, versao, titulo) contra tests/golden/metadados.json.

O golden foi escrito a mao a partir da capa de cada PDF (ver o campo 'fonte').
"""

import os

import pytest

from conftest import carregar_golden, extrair, pdf_da_nt

pytestmark = pytest.mark.golden

GOLDEN = {k: v for k, v in carregar_golden("metadados").items() if not k.startswith("_")} \
    if os.path.exists(os.path.join(os.path.dirname(__file__), "..", "golden", "metadados.json")) else {}


@pytest.mark.parametrize("nome", sorted(GOLDEN))
def test_metadados_conferem_com_o_golden(nome):
    esperado = GOLDEN[nome]
    dados = extrair(pdf_da_nt(nome), "nt")
    for campo in ("nt", "documento", "versao", "titulo"):
        assert dados[campo] == esperado[campo], (
            f"{nome}: {campo} = {dados[campo]!r}, esperado {esperado[campo]!r} "
            f"(fonte: pag. {esperado['fonte']['pagina']})"
        )


def test_golden_cobre_todas_as_nts_do_acervo():
    from conftest import listar_fontes

    nomes = {os.path.splitext(os.path.basename(p))[0] for p in listar_fontes("nt")}
    assert nomes <= set(GOLDEN), f"NTs sem golden de metadados: {sorted(nomes - set(GOLDEN))}"
