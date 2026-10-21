"""
Extracao de MOCs: mensagens completas, sem perda em relacao a extracao anterior, caminho portatil.

Pisos de quantidade em tests/golden/moc_minimos.json (extracao anterior a fase 2b).
"""

import json
import os
import re

import pytest

from conftest import GOLDEN, RAIZ, abrir_pdf, extrair, listar_fontes

from verificar_extracao import mensagem_truncada

pytestmark = [pytest.mark.golden, pytest.mark.lento]

MOCS = listar_fontes("moc")
NOMES = [os.path.splitext(os.path.basename(p))[0] for p in MOCS]

_minimos = GOLDEN / "moc_minimos.json"
MINIMOS = (
    {k: v for k, v in json.load(open(_minimos, encoding="utf-8")).items() if not k.startswith("_")}
    if _minimos.exists()
    else {}
)

# cStats que o PDF imprime depois de 'Obrig.' e que AINDA nao viram regra (lacuna conhecida, registrada em
# docs/duvidas-abertas.md). Qualquer outro cStat faltando faz o teste falhar.
LACUNAS_CONHECIDAS = {
    "MOC_CTe_VisaoGeral_v4.00": {"890"},
    "MOC_NFe_v7.00_VisaoGeral": {"831"},
}

# Mensagens conferidas no texto do PDF (multiplas linhas na coluna 'Descricao Erro')
MENSAGENS = [
    ("MOC_NFe_v7.00_VisaoGeral", "J05", "561", "Rejeição: Mês de Emissão informado na Chave de Acesso difere do Mês de Emissão da NF-e"),
    ("MOC_NFe_v7.00_VisaoGeral", "K02", "257", "Rejeição: Solicitante não habilitado para emissão da NF-e"),
]


@pytest.fixture(params=MOCS, ids=NOMES)
def moc(request):
    return request.param, extrair(request.param, "moc")


def test_nao_ha_menos_secoes_regras_e_campos_que_antes(moc):
    caminho, dados = moc
    nome = os.path.splitext(os.path.basename(caminho))[0]
    piso = MINIMOS.get(nome)
    if piso is None:
        pytest.skip(f"sem piso em moc_minimos.json para {nome}")
    obtido = {
        "secoes": dados["estatisticas"]["total_secoes"],
        "regras": len(dados.get("regras_validacao", [])),
        "campos": len(dados.get("campos_leiaute", [])),
    }
    menores = {k: (obtido[k], piso[k]) for k in piso if obtido[k] < piso[k]}
    assert not menores, f"{nome}: menos que a extracao anterior (obtido, piso): {menores}"


def test_mensagens_de_regra_nao_terminam_em_palavra_de_ligacao(moc):
    _, dados = moc
    ruins = [
        (r["id"], r["cStat"], r["mensagem"][-40:])
        for r in dados.get("regras_validacao", [])
        if mensagem_truncada(r.get("mensagem"), colchetes=False)
    ]
    assert not ruins, f"{len(ruins)} mensagens cortadas, ex.: {ruins[:3]}"


def test_mensagens_comecam_pelo_inicio(moc):
    _, dados = moc
    ruins = [(r["id"], r["mensagem"][:30]) for r in dados.get("regras_validacao", []) if r.get("mensagem") and r["mensagem"][0].islower()]
    assert not ruins, f"mensagem comeca em minuscula (palavra cortada): {ruins[:3]}"


def test_todo_cstat_impresso_depois_de_aplicacao_virou_regra(moc):
    caminho, dados = moc
    if not caminho.lower().endswith(".pdf"):
        pytest.skip("DOCX")
    doc = abrir_pdf(caminho)
    texto = " ".join(" ".join(p.get_text().split()) for p in doc)
    impressos = set(re.findall(r"\b(?:Obrig|Facult?|Futura)[.,]?\s+(\d{3,4})\b", texto))
    no_json = {r["cStat"] for r in dados.get("regras_validacao", [])}
    nome = os.path.splitext(os.path.basename(caminho))[0]
    faltando = impressos - no_json - LACUNAS_CONHECIDAS.get(nome, set())
    assert not faltando, f"cStat do PDF sem regra no JSON: {sorted(faltando)}"


def test_id_unico_e_unico(moc):
    _, dados = moc
    regras = dados.get("regras_validacao", [])
    ids = [r.get("id_unico") for r in regras]
    assert all(ids), "regra sem id_unico"
    assert len(set(ids)) == len(ids), "id_unico repetido"


def test_arquivo_origem_relativo(moc):
    caminho, dados = moc
    origem = dados["arquivo_origem"]
    assert not re.match(r"^[A-Za-z]:", origem) and "\\" not in origem, origem
    assert (RAIZ / origem).exists(), f"arquivo_origem nao existe a partir da raiz: {origem}"


@pytest.mark.parametrize("nome,id_,cstat,mensagem", MENSAGENS)
def test_mensagem_completa_conferida_no_pdf(nome, id_, cstat, mensagem):
    caminho = next((p for p in MOCS if os.path.basename(p).startswith(nome)), None)
    if caminho is None:
        pytest.skip(f"{nome} ausente em fontes/")
    regras = [
        r for r in extrair(caminho, "moc")["regras_validacao"] if r["id"] == id_ and r["cStat"] == cstat
    ]
    assert regras, f"regra {id_}/{cstat} nao encontrada"
    assert regras[0]["mensagem"] == mensagem


def test_docx_do_mdfe_tem_caminho_relativo():
    docx = next((p for p in MOCS if p.endswith("MOC_MDFe_Anexo_II_DAMDFE_v3.00b.docx")), None)
    if docx is None:
        pytest.skip("DOCX ausente")
    dados = extrair(docx, "moc")
    assert dados["arquivo_origem"] == "fontes/mdfe/moc/MOC_MDFe_Anexo_II_DAMDFE_v3.00b.docx"
    assert dados["estatisticas"]["total_secoes"] >= MINIMOS["MOC_MDFe_Anexo_II_DAMDFE_v3.00b"]["secoes"]
