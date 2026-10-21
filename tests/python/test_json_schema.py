"""Testes de utils/json_schema.py (validadores de NT e MOC)."""

import copy

from conftest import extrair, listar_fontes

from utils.json_schema import validate_moc_json, validate_nt_json

NT_OK = {
    "nt": "2026.007",
    "versao": "1.10",
    "documento": "NF-e",
    "titulo": "Emissao",
    "arquivo_origem": "fontes/nfe/notas-tecnicas/NT_2026_007_v1.10.pdf",
    "sha256": "abc",
    "extraido_em": "2026-10-20T00:00:00+00:00",
    "tipo_documento": "NT",
    "cronograma": [
        {"versao": "1.10", "homologacao": "Até 05/10/2026", "producao": "03/11/2026", "descricao": "x"}
    ],
    "secoes": [
        {
            "numero": "5.1",
            "titulo": "B",
            "tipo": "regras",
            "regras": [
                {
                    "id": "B02-10",
                    "id_unico": "5.1:B02-10",
                    "mensagem": "Rejeição: x",
                    "trechos": [{"texto": "a", "marcacao": "AMARELO"}],
                    "notas": [{"texto": "n", "marcacao": "SEM_MARCA", "trechos": [{"texto": "n", "marcacao": "SEM_MARCA"}]}],
                }
            ],
        }
    ],
}

MOC_OK = {
    "documento": "CT-e",
    "versao": "4.00",
    "tipo_documento": "MOC",
    "arquivo_origem": "fontes/cte/moc/MOC_CTe_VisaoGeral_v4.00.pdf",
    "sha256": "abc",
    "extraido_em": "2026-10-20T00:00:00+00:00",
    "regras_validacao": [{"id": "A04", "mensagem": "Rejeição: y", "trechos": [{"texto": "y", "marcacao": "SEM_MARCA"}]}],
}


def test_nt_valida_com_campos_novos():
    assert validate_nt_json(NT_OK) == (True, [])


def test_nt_versao_com_sufixo_e_valida():
    d = copy.deepcopy(NT_OK)
    d["versao"] = "1.14b"
    assert validate_nt_json(d)[0]


def test_nt_cronograma_vazio_e_valido():
    d = copy.deepcopy(NT_OK)
    d["cronograma"] = []
    assert validate_nt_json(d)[0]


def test_nt_rejeita_caminho_absoluto_e_barra_invertida():
    for ruim in ("C:\\Users\\x\\a.pdf", "C:/Users/x/a.pdf", "/home/x/a.pdf", "fontes\\nfe\\a.pdf"):
        d = copy.deepcopy(NT_OK)
        d["arquivo_origem"] = ruim
        ok, erros = validate_nt_json(d)
        assert not ok, ruim
        assert any("arquivo_origem" in e for e in erros)


def test_nt_rejeita_versao_mal_formada():
    d = copy.deepcopy(NT_OK)
    d["versao"] = "v1.0 b"
    assert not validate_nt_json(d)[0]


def test_nt_rejeita_cronograma_inventado():
    d = copy.deepcopy(NT_OK)
    d["cronograma"] = [{"versao": ".", "homologacao": "00/00/0000", "producao": ""}]
    ok, erros = validate_nt_json(d)
    assert not ok
    assert any("versao invalida" in e for e in erros)
    assert any("00/00/0000" in e for e in erros)


def test_nt_rejeita_trechos_malformados():
    d = copy.deepcopy(NT_OK)
    d["secoes"][0]["regras"][0]["trechos"] = [{"texto": "so texto"}]
    assert not validate_nt_json(d)[0]


def test_moc_valida_e_rejeita_caminho_absoluto():
    assert validate_moc_json(MOC_OK) == (True, [])
    d = copy.deepcopy(MOC_OK)
    d["arquivo_origem"] = "C:\\Users\\x\\a.pdf"
    assert not validate_moc_json(d)[0]


def test_extracao_real_de_moc_passa_no_schema():
    moc = next(p for p in listar_fontes("moc") if p.endswith("MOC_CTe_VisaoGeral_v4.00.pdf"))
    ok, erros = validate_moc_json(extrair(moc, "moc"))
    assert ok, erros


def test_extracao_real_de_nt_passa_no_schema_exceto_cronograma_ainda_nao_corrigido():
    """A estrutura/caminho/versao de uma NT real devem passar; o cronograma e coberto no grupo 3."""
    nt = next(p for p in listar_fontes("nt") if p.endswith("NT_2026_007_v1.10.pdf"))
    ok, erros = validate_nt_json(extrair(nt, "nt"))
    erros_nao_cronograma = [e for e in erros if not e.startswith("cronograma")]
    assert not erros_nao_cronograma, erros_nao_cronograma
