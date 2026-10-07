"""
utils/moc.py - Extracao estruturada de MOCs.

Produz:
- secoes: arvore hierarquica {numero, titulo, paragrafos?, subsecoes[]}
- regras_validacao: lista global {id, cStat, descricao, modelo, aplicacao, ...}
- campos_leiaute: lista global {seq, tag, nivel, descricao, ele, tipo, ocorrencia, ...}

Reaproveita a deteccao de titulos/cabecalhos/regras de utils/classificacao
(as linhas de regra do MOC tem o mesmo formato achatado das NTs).
"""

import re

from utils.classificacao import (
    _detectar_titulo,
    _montar_paragrafos,
    _tipo_header,
    parse_regra,
    PAT_ELLIPSIS,
    PAT_HEADER,
)

# ---------------------------------------------------------------------------
# Padroes de linha de leiaute (tabela achatada)
# ---------------------------------------------------------------------------
# Formato A (CT-e/MDF-e): "5 cUF 2 Código da UF do emitente do CTe. E N 1 - 1 2 D2 Utilizar..."
PAT_LAYOUT_A = re.compile(
    r"^(?P<seq>\d+)\s+(?P<tag>\S+)\s+(?P<nivel>\d+)\s+(?P<desc>.*?)\s+"
    r"(?P<ele>ES|CE|E|CG|A|G)\s+(?:(?P<tipo>N|C|D)\s+)?"
    r"(?P<ocor>\d+\s*-\s*[n\d])(?:\s+(?P<tail>.*))?$"
)

PAT_TAM = re.compile(r"^[\d\w-]+$")
PAT_DOM = re.compile(r"^(?:ER|D)\d+$")

# Formatos A/B no cabecalho (formato B e o da NF-e: "... Ele Pai Tipo Ocor.")
ELE_A = ("ES", "CE", "E", "CG", "A", "G")
ELE_B = ELE_A + ("ID", "RC")
TIPO_SET = ("N", "C", "D", "-")
OCOR_B = re.compile(r"^(?:- )?\d+-\d+$")


def _tail_leiaute(tail):
    """Reparte a cauda de uma linha de leiaute em (tamanho, dominio, observacao)."""
    parts = tail.split()
    tam = dom = ""
    obs = ""
    if not parts:
        return tam, dom, obs

    i = 0
    if re.match(r"^\d", parts[i]) and PAT_TAM.fullmatch(parts[i]):
        tam = parts[i]
        i += 1
        # "N - M" achatado em tres tokens
        if i + 1 < len(parts) and parts[i] == "-" and re.match(r"^\d", parts[i + 1]):
            tam += "-" + parts[i + 1]
            i += 2
    if i < len(parts) and PAT_DOM.fullmatch(parts[i]):
        dom = parts[i]
        i += 1
    if i < len(parts):
        obs = " ".join(parts[i:])
    return tam, dom, obs


def _parse_linha_campo_b(texto):
    """
    Parse de linha de leiaute formato NF-e (ancorado pela ocorrencia).

    Forma: "<id> <campo> <descricao>... <Ele> <Pai> [<Tipo>] <Ocor> [<Tam>] <Obs>"
    Ocor e compacto ("1-1" ou "- 1-1"); Ele pode ser A/E/G/CG/ES/CE/ID/RC.
    """
    tokens = texto.split()
    if len(tokens) < 5:
        return None

    # Localizar a ocorrencia compacta (ultimo token "N-N" possivel)
    k = -1
    for i, tok in enumerate(tokens):
        if OCOR_B.fullmatch(tok):
            k = i
    if k < 0 or k < 3:
        return None

    # Ele: primeiro token em ELE_B andando para tras a partir da ocorrencia
    ele_index = -1
    for j in range(k - 1, max(0, k - 5), -1):
        if tokens[j] in ELE_B:
            ele_index = j
            break
    if ele_index < 0:
        return None

    # Pai e Tipo: tokens entre Ele e Ocor (0 a 2)
    entre = tokens[ele_index + 1 : k]
    pai = entre[0] if entre else ""
    tipo = ""
    if len(entre) == 2:
        tipo = entre[1]
    elif len(entre) >= 2:
        pai = entre[0]
        tipo = entre[1] if entre[1] in TIPO_SET else ""

    resultado = {
        "texto": texto,
        "seq": tokens[0],
        "tag": tokens[1],
        "nivel": "",
        "descricao": " ".join(tokens[2:ele_index]),
        "ele": tokens[ele_index],
        "pai": pai,
        "tipo": tipo if tipo in TIPO_SET else "",
        "ocorrencia": tokens[k],
        "tamanho": "",
        "dominio": "",
        "observacao": "",
    }
    tail = " ".join(tokens[k + 1 :])
    if tail:
        tam, dom, obs = _tail_leiaute(tail)
        resultado["tamanho"] = tam
        resultado["dominio"] = dom
        resultado["observacao"] = obs
    return resultado


def _parse_linha_campo(texto, eh_formato_a):
    """Faz parse de uma linha de leiaute. Retorna dict ou None."""
    if eh_formato_a:
        m = PAT_LAYOUT_A.match(texto)
        if not m:
            return None
        resultado = {
            "texto": texto,
            "seq": m.group("seq"),
            "tag": m.group("tag"),
            "nivel": m.group("nivel"),
            "descricao": m.group("desc").strip(),
            "ele": m.group("ele"),
            "tipo": m.group("tipo") or "",
            "ocorrencia": re.sub(r"\s+", "", m.group("ocor")),
        }
        tail = m.group("tail")
        if tail:
            tam, dom, obs = _tail_leiaute(tail)
            resultado["tamanho"] = tam
            resultado["dominio"] = dom
            resultado["observacao"] = obs
        else:
            resultado["tamanho"] = ""
            resultado["dominio"] = ""
            resultado["observacao"] = ""
        return resultado

    return _parse_linha_campo_b(texto)


def montar_moc_estrutura(linhas, logger=None, permitir_numero_ponto=False):
    """
    Monta a estrutura hierarquica + regras + campos de um MOC.

    Args:
        linhas: lista de itens {text, marcacao, pagina}
        permitir_numero_ponto: True para MOCs em DOCX, que numeram
            secoes como "N. Titulo" (ex: "1. Introducao").

    Returns:
        dict com {'secoes', 'regras_validacao', 'campos_leiaute', 'estatisticas'}
    """
    secoes = []
    stack = []  # (depth, node)
    regras_validacao = []
    campos_leiaute = []

    modo = "texto"  # "texto" | "regras" | "layout"
    formato_layout = "A"  # heuristico; pode virar B com o cabecalho

    paragrafos = []  # acumulador de texto da secao corrente
    regra_atual = None
    campo_atual = None
    secao_atual = None
    grupo_atual = ""
    linhas_avulsas = []
    tem_regra = False  # alguma regra extraida no bloco atual?

    def no_atual():
        return stack[-1][1] if stack else None

    def nova_secao(numero, titulo):
        nonlocal paragrafos, regra_atual, campo_atual, grupo_atual, linhas_avulsas, modo, tem_regra
        depth = numero.count(".")
        node = {"numero": numero, "titulo": titulo}
        while stack and stack[-1][0] >= depth:
            stack.pop()
        if stack:
            pai = stack[-1][1]
            pai.setdefault("subsecoes", []).append(node)
        else:
            secoes.append(node)
        stack.append((depth, node))
        # Preparar estado novo
        if paragrafos:
            node["paragrafos"] = _montar_paragrafos(paragrafos)
        paragrafos = []
        regra_atual = None
        campo_atual = None
        grupo_atual = ""
        linhas_avulsas = []
        modo = "texto"
        tem_regra = False
        return node

    def fechar_modo():
        nonlocal paragrafos, regra_atual, campo_atual, linhas_avulsas, modo, tem_regra
        node = no_atual()
        if node and paragrafos:
            node.setdefault("paragrafos", []).extend(_montar_paragrafos(paragrafos))
        elif node and modo == "regras" and not tem_regra and linhas_avulsas:
            node.setdefault("paragrafos", []).extend(_montar_paragrafos(linhas_avulsas))
        paragrafos = []
        linhas_avulsas = []
        regra_atual = None
        campo_atual = None
        tem_regra = False

    for item in linhas:
        texto = item.get("text", "").strip()
        if len(texto) < 3:
            continue
        if PAT_ELLIPSIS.match(texto):
            continue
        marc = item.get("marcacao", "SEM_MARCA")
        pagina = item.get("pagina", 0)

        # Titulo de secao? (sempre, inclusive dentro de tabela)
        numero, titulo = _detectar_titulo(texto, em_tabela=(modo != "texto"), permitir_numero_ponto=permitir_numero_ponto)
        if numero is not None:
            fechar_modo()
            secao_atual = nova_secao(numero, titulo)
            continue

        # Cabecalho de tabela? ("# ...")
        if PAT_HEADER.match(texto):
            novo_tipo = _tipo_header(texto)  # "regras" | "tabela"
            novo_modo = "regras" if novo_tipo == "regras" else "layout"
            if modo != "texto" and novo_modo == modo:
                continue  # cabecalho repetido na virada de pagina
            fechar_modo()
            modo = novo_modo
            if modo == "layout":
                formato_layout = "B" if ("Pai" in texto or "ID Campo" in texto) else "A"
            continue

        # Demais logicas por modo
        if modo == "texto":
            if secao_atual is None:
                continue  # texto de capa antes da primeira secao
            paragrafos.append(item)
            continue

        if modo == "regras":
            regra = parse_regra(texto)
            if regra is not None and regra.get("cStat"):
                regra["marcacao"] = marc
                regra["pagina"] = pagina
                regra["grupo"] = grupo_atual
                regra["secao"] = (
                    {"numero": secao_atual["numero"], "titulo": secao_atual["titulo"]}
                    if secao_atual
                    else {}
                )
                regra["notas"] = []
                regra["descricao"] = regra.pop("condicao", "")
                regra_atual = regra
                regras_validacao.append(regra)
                tem_regra = True
            elif regra_atual is not None:
                regra_atual.setdefault("notas", []).append(
                    {"texto": texto, "marcacao": marc}
                )
            elif texto.startswith("#"):
                # Linha de grupo dentro da tabela de regras
                grupo_atual = texto[2:].strip()
            elif secao_atual is not None:
                # Prosa intercalada (ex: explicacao apos o ultimo bloco de regras)
                paragrafos.append(item)
            else:
                linhas_avulsas.append(item)
            continue

        # modo == "layout"
        campo = _parse_linha_campo(texto, formato_layout == "A")
        if campo is not None:
            campo["marcacao"] = marc
            campo["pagina"] = pagina
            campo["secao"] = (
                {"numero": secao_atual["numero"], "titulo": secao_atual["titulo"]}
                if secao_atual
                else {}
            )
            campos_leiaute.append(campo)
            campo_atual = campo
        elif campo_atual is not None:
            campo_atual["observacao"] = (campo_atual["observacao"] + " " + texto).strip()
        elif secao_atual is not None and not texto.startswith("#"):
            paragrafos.append(item)
        else:
            linhas_avulsas.append(item)

    fechar_modo()

    total_secoes = _contar_secoes(secoes)
    stats = {
        "total_secoes": total_secoes,
        "total_regras": len(regras_validacao),
        "total_campos": len(campos_leiaute),
        "por_marcacao": _contar_marcacoes(secoes, regras_validacao, campos_leiaute),
    }
    return {
        "secoes": secoes,
        "regras_validacao": regras_validacao,
        "campos_leiaute": campos_leiaute,
        "estatisticas": stats,
    }


def _contar_secoes(secoes):
    total = 0
    for sec in secoes:
        total += 1
        total += _contar_secoes(sec.get("subsecoes", []))
    return total


def _contar_marcacoes(secoes, regras, campos):
    cont = {"AMARELO": 0, "VERDE": 0, "EXCLUIDO": 0, "SEM_MARCA": 0}

    def _somar(itens):
        for it in itens:
            cont[it.get("marcacao", "SEM_MARCA")] = (
                cont.get(it.get("marcacao", "SEM_MARCA"), 0) + 1
            )

    def _por_secoes(lista):
        for sec in lista:
            _somar(sec.get("paragrafos", []))
            _por_secoes(sec.get("subsecoes", []))

    _por_secoes(secoes)
    _somar(regras)
    _somar(campos)
    return cont