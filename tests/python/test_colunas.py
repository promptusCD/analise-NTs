"""
Testes de utils/colunas.py: linearizacao de tabelas de regras por coluna.

Usa fixtures com os spans REAIS de paginas dos PDFs (tests/fixtures/spans_*.json,
geradas por scripts/python/gerar_fixtures_spans.py) e spans sinteticos.
"""

import json

import pytest

from conftest import RAIZ

from utils.colunas import detectar_fronteira_direita, linearizar_pagina

FIXTURES = RAIZ / "tests" / "fixtures"


def carregar(nome):
    caminho = FIXTURES / f"spans_{nome}.json"
    if not caminho.exists():
        pytest.skip(f"fixture ausente: {caminho}")
    dados = json.load(open(caminho, encoding="utf-8"))
    return dados["spans"], dados["largura"]


def sp(texto, x0, y, largura=60, size=8.0, marcacao="SEM_MARCA"):
    """Span sintetico."""
    return {"text": texto, "bbox": [x0, y, x0 + largura, y + 8], "size": size, "marcacao": marcacao, "bold": False}


def achar(itens, comeca_com):
    achados = [i for i in itens if i["text"].startswith(comeca_com)]
    assert achados, f"item que comeca com {comeca_com!r} nao encontrado"
    return achados[0]


# ---------------------------------------------------------------------------
# Paginas reais
# ---------------------------------------------------------------------------
def test_nt2026007_p9_mensagem_completa_na_linha_canonica():
    spans, largura = carregar("nt2026007_p9")
    itens = linearizar_pagina(spans, largura, {"em_regra": False})
    regra = achar(itens, "5AF15-12")
    assert regra["text"].endswith("Rejeição: IE do local de retirada não está ativa na UF")
    assert "Obrig. 167 Rej." in regra["text"]


def test_nt2026007_p9_mensagem_que_quebra_em_duas_linhas():
    spans, largura = carregar("nt2026007_p9")
    itens = linearizar_pagina(spans, largura, {"em_regra": False})
    regra = achar(itens, "12C02-10")
    assert "Rejeição: CNPJ [XX.XXX.XXX/XXXX-DV] do emitente não cadastrado na Receita Federal" in regra["text"]


def test_nt2026007_p9_notas_nao_recebem_texto_da_mensagem():
    """5AF15-11: 'irregular na UF' (coluna da direita) vai para a mensagem, nao para a nota."""
    spans, largura = carregar("nt2026007_p9")
    itens = linearizar_pagina(spans, largura, {})
    regra = achar(itens, "5AF15-11")
    assert regra["text"].endswith("Rejeição: IE do Local de Retirada com situação irregular na UF")
    observacoes = [i for i in itens if i["text"].startswith("Observação:")]
    assert observacoes
    for o in observacoes:
        assert o["text"] in (
            "Observação: Regra de validação para todas as SEFAZ Autorizadoras.",
            "Observação: Regra de validação para todas as autorizadoras.",
        ), o["text"]


def test_continuacao_de_regra_que_quebra_entre_paginas():
    """Topo da pagina seguinte: o lado direito e continuacao da mensagem; o esquerdo, nota."""
    pagina1 = tabela_sintetica()
    pagina1 += [sp("Página", 700, 800, 30), sp("1", 735, 800, 5), sp("/ 2", 745, 800, 15)]
    estado = {}
    linearizar_pagina(pagina1, 842, estado)
    assert estado["em_regra"] is True, "o rodape nao pode encerrar a regra: ela pode continuar na pagina seguinte"

    pagina2 = [
        sp("Projeto", 40, 24, 40, size=8), sp("Nota Fiscal Eletrônica", 40, 33, 100, size=10),
        sp("Observação: vale tambem", 120, 70, 120), sp("para a UF", 545, 70, 60),
    ]
    itens = linearizar_pagina(pagina2, 842, estado)
    continuacoes = [i for i in itens if i.get("continuacao_mensagem")]
    assert [c["text"] for c in continuacoes] == ["para a UF"]
    assert any(i["text"] == "Observação: vale tambem" for i in itens)
    assert [i["text"] for i in itens if i["text"] in ("Projeto", "Nota Fiscal Eletrônica")] == ["Projeto", "Nota Fiscal Eletrônica"]
    assert not any(i.get("continuacao_mensagem") for i in itens if i["text"] in ("Projeto", "Nota Fiscal Eletrônica"))


def test_cabecalho_repetido_da_pagina_anterior_nao_vira_continuacao():
    """Linhas do topo iguais as da pagina anterior (cabecalho corrente) nunca sao tratadas como continuacao."""
    cab = [sp("Projeto", 40, 60, 40, size=8), sp("Nota Fiscal Eletrônica", 560, 70, 100, size=10)]  # y>50 de proposito
    estado = {}
    linearizar_pagina(tabela_sintetica() + cab, 842, estado)
    itens = linearizar_pagina(cab, 842, estado)
    assert not any(i.get("continuacao_mensagem") for i in itens), [i["text"] for i in itens]


def test_nt2026008_p7_cabecalho_sem_hashtag_ganha_prefixo_e_regra_sem_efeito():
    spans, largura = carregar("nt2026008_p7")
    itens = linearizar_pagina(spans, largura, {})
    cabecalho = [i for i in itens if "Regra de Validação" in i["text"] and "Aplic" in i["text"]]
    assert cabecalho and cabecalho[0]["text"].startswith("# ")
    regra = achar(itens, "B25-80")
    assert regra["text"].startswith("B25-80 55 Se finalidade da NF-e")
    assert "Obrig. 1001 Rejeição: NF-e com finalidade de" in regra["text"]
    assert "somente para IBS/CBS" in regra["text"], "continuacao da mensagem (coluna direita) nao foi anexada"


def test_cte2026004_p8_regra_com_notas_a_esquerda():
    spans, largura = carregar("cte2026004_p8")
    itens = linearizar_pagina(spans, largura, {})
    regra = achar(itens, "01 O total geral do DFe")
    assert "Obrig. 365 Rej. Rejeição: Total do DFe inválido" in regra["text"]
    # as linhas seguintes da coluna esquerda viram itens proprios (notas)
    assert any(i["text"].startswith("Exceção:") for i in itens)


def test_marcacao_por_trecho_na_linha_canonica():
    spans, largura = carregar("cte2026004_p8")
    itens = linearizar_pagina(spans, largura, {})
    regra = achar(itens, "01 O total geral do DFe")
    # a condicao esta riscada (EXCLUIDO) e a mensagem nao: a linha reflete o trecho mais relevante
    assert regra["marcacao"] == "EXCLUIDO"
    assert {t["marcacao"] for t in regra["trechos"]} >= {"EXCLUIDO", "SEM_MARCA"}


# ---------------------------------------------------------------------------
# Spans sinteticos
# ---------------------------------------------------------------------------
def tabela_sintetica(com_hashtag=True):
    h = "#" if com_hashtag else "Campo"
    return [
        sp(h, 40, 100, 10), sp("Regra de Validação", 120, 100, 80), sp("Aplic.", 400, 100, 30),
        sp("Msg", 450, 100, 20), sp("Efeito", 490, 100, 30), sp("Descrição Erro", 540, 100, 70),
        sp("A01-10", 40, 120, 40), sp("55", 90, 120, 10), sp("Se campo X for informado:", 120, 120, 150),
        sp("Obrig.", 402, 120, 30), sp("101", 452, 120, 15), sp("Rej.", 492, 120, 20),
        sp("Rejeição: campo X", 540, 120, 90),
        sp("- Acessar o cadastro", 120, 130, 100), sp("invalido na base", 545, 130, 80),
        sp("Observação: vale para todas.", 120, 140, 130, marcacao="AMARELO"),
        sp("A01-20", 40, 160, 40), sp("55", 90, 160, 10), sp("Se campo Y:", 120, 160, 80),
        sp("Facult.", 402, 160, 30), sp("102", 452, 160, 15), sp("Rejeição: campo Y", 540, 160, 90),
    ]


def test_sintetico_mensagem_nao_vaza_para_notas():
    itens = linearizar_pagina(tabela_sintetica(), 842, {})
    a = achar(itens, "A01-10")
    assert a["text"] == "A01-10 55 Se campo X for informado: Obrig. 101 Rej. Rejeição: campo X invalido na base"
    notas = [i["text"] for i in itens if i["text"].startswith(("- Acessar", "Observação"))]
    assert notas == ["- Acessar o cadastro", "Observação: vale para todas."]
    b = achar(itens, "A01-20")
    assert b["text"] == "A01-20 55 Se campo Y: Facult. 102 Rejeição: campo Y"


def test_sintetico_cabecalho_sem_hashtag():
    itens = linearizar_pagina(tabela_sintetica(com_hashtag=False), 842, {})
    cab = [i for i in itens if "Regra de Validação" in i["text"]][0]
    assert cab["text"].startswith("# Campo")


def test_sintetico_cabecalho_com_hashtag_nao_duplica():
    itens = linearizar_pagina(tabela_sintetica(), 842, {})
    cab = [i for i in itens if "Regra de Validação" in i["text"]][0]
    assert cab["text"].startswith("# Regra") or cab["text"].startswith("#")
    assert not cab["text"].startswith("# #")


def test_sintetico_trecho_amarelo_define_marcacao_da_nota():
    itens = linearizar_pagina(tabela_sintetica(), 842, {})
    nota = achar(itens, "Observação")
    assert nota["marcacao"] == "AMARELO"
    assert nota["trechos"] == [{"texto": "Observação: vale para todas.", "marcacao": "AMARELO"}]


def test_sintetico_rodape_nao_e_engolido_pela_regra():
    spans = tabela_sintetica() + [sp("Página", 700, 800, 30), sp("3", 735, 800, 5), sp("/ 9", 745, 800, 15)]
    itens = linearizar_pagina(spans, 842, {})
    a = achar(itens, "A01-20")
    assert "Página" not in a["text"] and "/ 9" not in a["text"]
    assert any(i["text"] == "Página 3 / 9" for i in itens)


def test_sintetico_sem_tabela_de_regras_mantem_linhas_por_y():
    spans = [sp("Texto livre", 50, 100, 60), sp("com duas partes", 120, 100, 80), sp("Outra linha", 50, 120, 60)]
    itens = linearizar_pagina(spans, 842, {})
    assert [i["text"] for i in itens] == ["Texto livre com duas partes", "Outra linha"]


def _aplic(x, y, cstat="101"):
    """Aplic. + cStat lado a lado (a assinatura de uma linha de regra)."""
    return [sp("Obrig.", x, y, 30), sp(cstat, x + 45, y, 15)]


def test_fronteira_ignora_ocorrencia_solta_no_texto():
    spans = [s for y in (100, 120, 140) for s in _aplic(400, y)] + _aplic(380, 160)
    assert detectar_fronteira_direita(spans, 842) == pytest.approx(380 - 6)  # 380 esta perto da mediana
    solto = _aplic(60, 90)  # texto corrido no inicio da linha
    assert detectar_fronteira_direita(spans + solto, None) == pytest.approx(380 - 6)
    assert detectar_fronteira_direita(solto, 842) is None  # fora do primeiro terco da pagina


def test_palavra_de_aplicacao_sem_cstat_nao_e_linha_de_regra():
    """MOC, coluna Observacao do leiaute: 'opcional.' / 'Futura' no inicio da linha NAO sao regras."""
    spans = [
        sp("128", 40, 100, 20), sp("CPF", 70, 100, 30), sp("Número do CPF", 110, 100, 90),
        sp("E", 420, 100, 8), sp("C", 450, 100, 8), sp("1 - 1", 480, 100, 25), sp("ER10", 520, 100, 25),
        sp("opcional.", 560, 100, 50), sp("Futura implementação", 560, 109, 100),
        sp("129", 40, 120, 20), sp("infSeg", 70, 120, 40),
    ]
    assert detectar_fronteira_direita(spans, 842) is None
    itens = linearizar_pagina(spans, 842, {})
    assert not any(i.get("sintetico") for i in itens), "criou cabecalho de regras em tabela de leiaute"
    assert [i["text"] for i in itens][0].startswith("128 CPF Número do CPF E C 1 - 1 ER10 opcional.")


def test_titulo_encerra_a_regra_corrente():
    spans = tabela_sintetica() + [sp("5.3 Nova secao", 40, 200, 100, size=14), sp("texto depois", 120, 220, 60)]
    itens = linearizar_pagina(spans, 842, {})
    textos = [i["text"] for i in itens]
    assert "5.3 Nova secao" in textos and "texto depois" in textos
    assert "texto depois" not in achar(itens, "A01-20")["text"]


def test_tabela_de_regras_sem_cabecalho_ganha_cabecalho_sintetico():
    """MDF-e: regra sem linha de cabecalho; o classificador so entra em modo 'regras' com um '#'."""
    spans = [
        sp("Se modal rodoviário e tipo do", 86, 181, 150), sp("Obrig.", 302, 181, 30),
        sp("684", 338, 181, 15), sp("Rej.", 369, 181, 20), sp("Rejeição: CIOT deverá ser informado", 403, 181, 150),
        sp("emitente igual a prestador", 86, 193, 120),
    ]
    itens = linearizar_pagina(spans, 595, {})
    assert itens[0]["text"] == "# Regra de Validação" and itens[0].get("sintetico")
    assert itens[1]["text"].startswith("Se modal rodoviário e tipo do Obrig. 684 Rej. Rejeição: CIOT")


def test_cabecalho_real_nao_gera_cabecalho_sintetico():
    itens = linearizar_pagina(tabela_sintetica(), 842, {})
    assert not any(i.get("sintetico") for i in itens)


def test_cabecalho_sintetico_so_uma_vez_por_tabela_e_de_novo_apos_titulo():
    def regra(y, id_, cstat):
        return [sp(id_, 40, y, 40), sp("Se X:", 120, y, 60), sp("Obrig.", 402, y, 30), sp(cstat, 452, y, 15),
                sp("Rejeição: X", 540, y, 60)]
    spans = regra(100, "A01-10", "101") + regra(120, "A01-20", "102")
    spans += [sp("6 Nova secao", 40, 160, 100, size=14)] + regra(200, "B01-10", "201")
    itens = linearizar_pagina(spans, 842, {})
    sinteticos = [k for k, i in enumerate(itens) if i.get("sintetico")]
    assert len(sinteticos) == 2, [i["text"] for i in itens]
    assert itens[sinteticos[0] + 1]["text"].startswith("A01-10")
    assert itens[sinteticos[1] + 1]["text"].startswith("B01-10")


def test_ponto_solto_da_coluna_efeito_nao_vai_para_a_mensagem():
    """'Rej' / '.' quebrado em duas linhas na coluna estreita Efeito (G103 da CT-e 2026.004)."""
    spans = [
        sp("G103", 40, 100, 30), sp("Se tipo de emissão:", 76, 100, 100), sp("Obrig.", 281, 100, 30),
        sp("228", 317, 100, 15), sp("Rej", 344, 100, 15), sp("Rejeição: Data de Emissão muito atrasada", 367, 100, 150),
        sp(".", 344, 109, 3),
        sp("Data-Hora de Emissão com atraso", 76, 109, 140),
    ]
    itens = linearizar_pagina(spans, 595, {})
    regra = achar(itens, "G103")
    assert regra["text"].endswith("Rej Rejeição: Data de Emissão muito atrasada"), regra["text"]
    assert any(i["text"] == "Data-Hora de Emissão com atraso" for i in itens)


def test_ponto_final_da_mensagem_continua_na_mensagem():
    """Um '.' no FIM da mensagem (span separado apos trecho riscado) e conteudo, nao ruido da coluna Efeito."""
    spans = [
        sp("G008", 40, 100, 30), sp("Se forma de emissão:", 76, 100, 100), sp("Obrig.", 281, 100, 30),
        sp("586", 317, 100, 15), sp("Rej", 344, 100, 15), sp("Rejeição: Data e Justificativa", 367, 100, 150),
        sp(".", 344, 109, 3),
        sp("tipo de emissão diferente de FS-DA", 367, 118, 150), sp(".", 520, 118, 3),
    ]
    regra = achar(linearizar_pagina(spans, 595, {}), "G008")
    assert regra["text"].endswith("tipo de emissão diferente de FS-DA ."), regra["text"]
    assert " Rej Rejeição" in regra["text"] and "Rej . Rejeição" not in regra["text"]


def test_ponto_final_apos_linha_de_continuacao_mais_a_direita():
    """O inicio da mensagem vem da 1a linha: uma continuacao que comeca mais a direita nao o desloca."""
    spans = [
        sp("G008", 40, 100, 30), sp("Se forma de emissão:", 76, 100, 100), sp("Obrig.", 281, 100, 30),
        sp("586", 317, 100, 15), sp("Rej", 344, 100, 15), sp("Rejeição: Data e Justificativa", 367, 100, 150),
        sp(".", 344, 109, 3),
        sp("tipo de emissão", 367, 118, 80), sp("de Contingência", 459, 118, 80),
        sp("Offline", 367, 127, 40), sp("FS-DA", 410, 127, 30), sp(".", 442, 127, 3),
    ]
    regra = achar(linearizar_pagina(spans, 595, {}), "G008")
    assert regra["text"].endswith("Offline FS-DA ."), regra["text"]


def test_aplicacao_dentro_do_span_da_esquerda_ainda_inicia_a_regra():
    """MOC NF-e: 'Facul.' vem no fim do span longo da coluna Regra; so o cStat fica na direita."""
    spans = [
        sp("# Regra de Validação Aplic. Msg Efeito Descrição Erro", 40, 80, 300),
        # uma linha "normal" da mesma pagina (Obrig. como span proprio) define a fronteira de coluna
        sp("D01", 55, 90, 20), sp("Verifica Schema", 91, 90, 100), sp("Obrig.", 405, 90, 24),
        sp("215", 438, 90, 14), sp("Rej.", 465, 90, 16), sp("Rejeição: Falha no schema", 491, 90, 150),
        sp("D01a", 55, 100, 20), sp("Em caso de Falha de Schema, verificar se existe a tag raiz Facul.", 91, 100, 337),
        sp("565", 438, 100, 14), sp("Rej.", 465, 100, 16), sp("Rejeição: Falha no schema XML", 491, 100, 200),
        sp("D01b", 55, 112, 20), sp("Em caso de Falha, verificar o atributo versao Facul.", 91, 112, 300),
        sp("568", 438, 112, 14), sp("Rej.", 465, 112, 16), sp("Rejeição: Falha no schema da versao", 491, 112, 200),
        sp("mensagem", 91, 122, 40), sp("e", 491, 122, 6),
    ]
    itens = linearizar_pagina(spans, 842, {})
    assert not any(i.get("sintetico") for i in itens), "a tabela ja tinha cabecalho"
    d1 = achar(itens, "D01a")
    assert d1["text"].endswith("Facul. 565 Rej. Rejeição: Falha no schema XML"), d1["text"]
    d2 = achar(itens, "D01b")
    assert d2["text"].endswith("Rejeição: Falha no schema da versao e"), d2["text"]
    assert any(i["text"] == "mensagem" for i in itens)
