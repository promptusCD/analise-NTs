"""Testes de utils/classificacao.py (montagem de secoes tipificadas)."""

from utils.classificacao import montar_secoes_typed, parse_regra


def linha(texto, pagina=1, **extra):
    d = {"text": texto, "marcacao": "SEM_MARCA", "pagina": pagina}
    d.update(extra)
    return d


def test_parse_regra_sem_coluna_efeito_preserva_a_mensagem():
    """'Obrig. 1001 Rejeicao: ...' (NT 2026.008): 'Rej' de 'Rejeicao' NAO e o efeito."""
    r = parse_regra("B25-80 55 Se finalidade igual a credito Obrig. 1001 Rejeição: NF-e com finalidade")
    assert r["efeito"] == ""
    assert r["mensagem"] == "Rejeição: NF-e com finalidade"
    assert r["cStat"] == "1001"


def test_parse_regra_com_efeito_continua_funcionando():
    r = parse_regra("001 Se CST informado Obrig. 311 Rej. Rejeição: CST invalido")
    assert (r["efeito"], r["mensagem"], r["cStat"]) == ("Rej", "Rejeição: CST invalido", "311")


def test_parse_regra_aplicacao_abreviada():
    """'Facul.' (K01-10 da NT 2026.002) e uma aplicacao valida."""
    r = parse_regra("K01-10 55 Informado NCM de medicamento Facul. 840 Rej. Rejeição: NCM de medicamento")
    assert r is not None and r["aplicacao"] == "Facul" and r["cStat"] == "840"


def test_continuacao_de_mensagem_entre_paginas_vai_para_a_mensagem():
    itens = [
        linha("# Modelo Regra de Validação Aplic. Msg Efeito Descrição Erro"),
        linha("A01-10 55 Se campo X: Obrig. 101 Rej. Rejeição: campo X", pagina=1),
        linha("Observação: vale para todas.", pagina=1),
        linha("invalido na base", pagina=2, continuacao_mensagem=True),
        linha("Observação: segunda nota.", pagina=2),
    ]
    secoes = montar_secoes_typed(itens)
    regras = [r for s in secoes if s["tipo"] == "regras" for r in s["regras"]]
    assert len(regras) == 1
    assert regras[0]["mensagem"] == "Rejeição: campo X invalido na base"
    assert [n["texto"] for n in regras[0]["notas"]] == ["Observação: vale para todas.", "Observação: segunda nota."]
    assert "invalido na base" in regras[0]["texto_completo"]


def _regras(secoes):
    return [r for s in secoes if s["tipo"] == "regras" for r in s["regras"]]


def test_id_unico_distingue_ids_repetidos_entre_tabelas():
    itens = [
        linha("2 Exigência IBS"),
        linha("# Regra de Validação Aplic. cStat Efeito Mensagem"),
        linha("001 Se X Obrig. 310 Rej. Rejeição: X"),
        linha("3 Totais"),
        linha("# Regra de Validação Aplic. cStat Efeito Mensagem"),
        linha("001 Se Y Obrig. 348 Rej. Rejeição: Y"),
        linha("002 Se Z Obrig. 349 Rej. Rejeição: Z"),
    ]
    regras = _regras(montar_secoes_typed(itens))
    assert [r["id"] for r in regras] == ["001", "001", "002"]
    assert [r["id_unico"] for r in regras] == ["2:001", "3:001", "3:002"]
    assert [r["cStat"] for r in regras] == ["310", "348", "349"]


def test_id_unico_repetido_na_mesma_secao_ganha_sufixo():
    itens = [
        linha("3 Totais"),
        linha("# Regra de Validação Aplic. cStat Efeito Mensagem"),
        linha("001 Se X Obrig. 310 Rej. Rejeição: X"),
        linha("# Regra de Validação Aplic. cStat Efeito Mensagem Outra"),
        linha("001 Se Y Obrig. 348 Rej. Rejeição: Y"),
    ]
    ids = [r["id_unico"] for r in _regras(montar_secoes_typed(itens))]
    assert len(set(ids)) == len(ids) == 2


def test_linha_de_leiaute_com_elemento_de_escolha_cg():
    """CT-e: 'CG' (grupo de escolha) e elemento valido; a linha nao pode virar texto."""
    from utils.classificacao import parse_linha_tabela

    r = parse_linha_tabela("gICMSPrevistoPagtoAntecip CG imp/ICMS G 0-1 - Grupo utilizado exclusivamente na", [])
    assert r is not None and r["ele"] == "CG" and r["pai"] == "imp/ICMS" and r["ocorrencia"] == "0-1"
    r = parse_linha_tabela("vICMSPrevisto E gICMSPrevistoPagtoAntecip E 1-1 13v2 Valor do ICMS a incidir", [])
    assert r is not None and r["ele"] == "E" and r["tipo"] == "E"


def test_tabela_de_leiaute_com_cg_nao_perde_a_linha_seguinte():
    itens = [
        linha("3 Alterações no Leiaute"),
        linha("# Campo Ele Pai Tipo Ocor. Tam. Descrição/Observação"),
        linha("gICMSPrevisto CG imp/ICMS G 0-1 - Grupo utilizado"),
        linha("determinação da BC em"),
        linha("vICMSPrevisto E gICMSPrevisto E 1-1 13v2 Valor do ICMS"),
    ]
    tabelas = [s for s in montar_secoes_typed(itens) if s["tipo"] == "tabela"]
    assert len(tabelas) == 1 and len(tabelas[0]["linhas"]) == 2
