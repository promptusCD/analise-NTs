"""
Invariantes gerais da extracao de NTs (valem para QUALQUER NT do acervo).

Cada teste extrai o PDF em memoria (sem escrever no repositorio) e compara com
propriedades calculadas de forma independente do extrator (texto bruto do PDF).
"""

import os
import re

import pytest

from conftest import abrir_pdf, extrair, listar_fontes

from verificar_extracao import (
    PAT_ID_LINHA,
    PAT_NOTA_COLADA,
    cronograma_invalido,
    mensagem_truncada,
    regras_da_nt,
)

NTS = listar_fontes("nt")
IDS = [os.path.basename(p) for p in NTS]

pytestmark = pytest.mark.golden


@pytest.fixture(params=NTS, ids=IDS)
def nt(request):
    caminho = request.param
    return caminho, extrair(caminho, "nt")


def test_ids_de_regra_do_pdf_estao_no_json(nt):
    caminho, dados = nt
    doc = abrir_pdf(caminho)
    texto = "\n".join(p.get_text() for p in doc)
    ids_pdf = set(PAT_ID_LINHA.findall(texto))
    if not ids_pdf:
        pytest.skip("NT sem IDs de regra no padrao NF-e (regras numericas ou sem regras)")
    ids_json = {r["id"] for r in regras_da_nt(dados)}
    assert ids_pdf - ids_json == set(), f"IDs do PDF ausentes no JSON: {sorted(ids_pdf - ids_json)}"


def test_mensagens_nao_truncadas(nt):
    _, dados = nt
    ruins = [(r["id"], r["mensagem"]) for r in regras_da_nt(dados) if mensagem_truncada(r.get("mensagem"))]
    assert not ruins, f"{len(ruins)} mensagens truncadas, ex.: {ruins[:3]}"


def test_mensagens_comecam_pelo_inicio(nt):
    """Mensagem nunca comeca em minuscula: seria o 'resto' de uma palavra cortada (ex.: 'eicao: ...')."""
    _, dados = nt
    ruins = [
        (r["id"], r["mensagem"][:30])
        for r in regras_da_nt(dados)
        if r.get("mensagem") and r["mensagem"][0].islower()
    ]
    assert not ruins, f"{len(ruins)} mensagens comecam em minuscula, ex.: {ruins[:3]}"


def test_notas_sem_fragmento_de_mensagem(nt):
    _, dados = nt
    ruins = []
    for r in regras_da_nt(dados):
        for n in r.get("notas", []):
            if PAT_NOTA_COLADA.search((n.get("texto") or "").strip()):
                ruins.append((r["id"], n["texto"][-60:]))
    assert not ruins, f"{len(ruins)} notas terminam em fragmento, ex.: {ruins[:3]}"


def test_arquivo_origem_relativo(nt):
    _, dados = nt
    origem = dados["arquivo_origem"]
    assert not re.match(r"^[A-Za-z]:", origem), f"caminho absoluto: {origem}"
    assert "\\" not in origem, f"separador de Windows no caminho: {origem}"
    assert origem.startswith("fontes/"), origem


def test_cronograma_sem_valores_invalidos(nt):
    _, dados = nt
    assert dados["cronograma"], "cronograma vazio (ERRO_DATA_NAO_ENCONTRADA)"
    assert cronograma_invalido(dados["cronograma"]) == []


def test_id_unico_e_unico_e_preserva_id_e_cstat(nt):
    _, dados = nt
    regras = regras_da_nt(dados)
    ids_unicos = [r.get("id_unico") for r in regras]
    assert all(ids_unicos), "regra sem id_unico"
    assert len(set(ids_unicos)) == len(ids_unicos), "id_unico repetido"
    for r in regras:
        chave = r["id_unico"].split(":", 1)[1].split("#")[0]
        assert chave == (r["id"] or f"cStat{r['cStat']}"), (r["id"], r["id_unico"])


def test_todo_cstat_impresso_depois_de_aplicacao_virou_regra(nt):
    """
    Independente do extrator: todo cStat que o PDF imprime logo depois de 'Obrig.'/'Facult.'
    (coluna Aplic. -> cStat) precisa estar em alguma regra do JSON - com ou sem coluna de ID.
    """
    caminho, dados = nt
    doc = abrir_pdf(caminho)
    texto = " ".join(" ".join(p.get_text().split()) for p in doc)
    impressos = set(re.findall(r"\b(?:Obrig|Facult?|Futura)[.,]?\s+(\d{3,4})\b", texto))
    no_json = {r["cStat"] for r in regras_da_nt(dados)}
    assert impressos - no_json == set(), f"cStat do PDF sem regra no JSON: {sorted(impressos - no_json)}"
