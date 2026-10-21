"""Testes de utils/saida.py: caminhos portaveis no JSON."""

import json
import re

from conftest import RAIZ, extrair, listar_fontes

from utils.saida import caminho_relativo, gerar_json_moc, gerar_json_nt


def test_caminho_relativo_dentro_da_raiz():
    absoluto = RAIZ / "fontes" / "nfe" / "notas-tecnicas" / "NT_2026_007_v1.10.pdf"
    assert caminho_relativo(absoluto) == "fontes/nfe/notas-tecnicas/NT_2026_007_v1.10.pdf"


def test_caminho_relativo_aceita_raiz_explicita(tmp_path):
    arquivo = tmp_path / "fontes" / "cte" / "moc" / "x.pdf"
    assert caminho_relativo(arquivo, raiz=tmp_path) == "fontes/cte/moc/x.pdf"


def test_caminho_fora_da_raiz_vira_so_o_nome(tmp_path):
    assert caminho_relativo(tmp_path / "solto.pdf") == "solto.pdf"


def test_gerar_json_nt_e_moc_gravam_caminho_relativo():
    absoluto = str(RAIZ / "fontes" / "mdfe" / "moc" / "MOC_MDFe_VisaoGeral_v3.00b.pdf")
    nt = gerar_json_nt({}, [], [], absoluto, "h")
    moc = gerar_json_moc({}, [], [], [], absoluto, "h")
    for dados in (nt, moc):
        assert dados["arquivo_origem"] == "fontes/mdfe/moc/MOC_MDFe_VisaoGeral_v3.00b.pdf"
        assert not re.match(r"^[A-Za-z]:", dados["arquivo_origem"])


def test_nenhum_json_extraido_contem_caminho_de_usuario():
    pdf = next(p for p in listar_fontes("nt") if p.endswith("MDFe_NT_2026_001_v1.00.pdf"))
    texto = json.dumps(extrair(pdf, "nt"), ensure_ascii=False)
    assert "Users" not in texto and ":\\\\" not in texto
