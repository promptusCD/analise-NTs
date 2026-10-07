"""
utils/classificacao.py - Classifica linhas de NTs em secoes tipificadas.

Tipos de secao:
- "tabela": cabecalho[] + linhas[] (tabela de leiaute)
- "regras": regras[] de validacao com campos estruturados
- "texto":   paragrafos[] de texto corrido

A IA le o JSON gerado e produz o MD legivel.
"""

import re

# ---------------------------------------------------------------------------
# Padroes de cabecalho de tabela (linha comeca com "#")
# ---------------------------------------------------------------------------
PAT_HEADER = re.compile(r"^#\s+(\S.*)$")

# ---------------------------------------------------------------------------
# Padroes de titulo de secao
# ---------------------------------------------------------------------------
# Subsecao: "4.1 Grupo C. Identificacao do Emitente...", "2.1 Leiaute de Impressao..."
PAT_SUB = re.compile(r"^(\d+(?:\.\d+)+)\s+([A-ZÀ-Ú].+)$")
# Secao top-level: "1 Resumo", "5 Validacoes dos campos..."
PAT_TOP = re.compile(r"^(\d{1,2})\s+([A-ZÀ-Ú].+)$")
# Variantes usadas so para MOCs em DOCX (numeracao "N. Titulo", ex: "1. Introducao")
PAT_SUB_COM_PONTO = re.compile(r"^(\d+(?:\.\d+)+)\.\s+([A-ZÀ-Ú].+)$")
PAT_TOP_COM_PONTO = re.compile(r"^(\d{1,2})\.\s+([A-ZÀ-Ú].+)$")
# Numeracao "N." de item de lista/procedimento (ex: "1. Campo C17 - ...")
PAT_NUMERO_PONTO_LISTA = re.compile(
    r"^(Campo\s+[A-Z]|RV\b|Inclu|Alterad|Exce|Melhoria|Orienta|Restri|Solicitar|Obter|Informar|Gerar|Imprimir|Providenciar|No\s|O\s+PAA|PAA\b)"
)

# Linha de tabela: token avulso E/G seguido de pai e ocorrencia (ex: "G A01 1-1")
PAT_ROW_SHAPE = re.compile(r"\s[EG]\s+\S+\s+(?:[A-Za-z0-9]+\s+)?\d+-\d+")
# Linha de leiaute de MOC: "... Ele [Pai] [Tipo] Ocor"
# (ex: "7 CFOP 2 ... E C 1 - 1 4 ER51", "93 ICMS00 ... do CG 1 - 1")
PAT_MOC_ROW = re.compile(
    r"\s(?:ES|CE|E|CG|A|G)\s+(?:\S+\s+){0,2}\d+\s*-\s*[n\d]"
)
# Titulo com cara de conteudo de celula: "D2 Utilizar...", "C17 IE..."
PAT_TAG_PREFIX = re.compile(r"^[A-Za-z]{1,3}\d")

# Elision de linhas de tabela: "... ... ..."
PAT_ELLIPSIS = re.compile(r"^[\s.\-…]+$")

# ---------------------------------------------------------------------------
# Padroes de regra de validacao (linha achatada de tabela)
# Ids: "001", "P12-40", "1P10-30", "UB12-11", "5E17-70"
# ---------------------------------------------------------------------------
PAT_REGRA_INICIO = re.compile(r"^([A-Za-z]{0,3}\d[\w-]*)\s+(.*)$")
PAT_MODELO = re.compile(r"^(\d{2}(?:/\d{2})+)\s+(.*)$")
PAT_APLICACAO = re.compile(r"\b(Obrig\.?|Facult\.?|Facultativa|Futura|Opcional)\b")
PAT_CSTAT = re.compile(r"\b(\d{3,4})\b")
PAT_EFEITO = re.compile(r"^\s*(Rej\.?|Aceito\.?|Aceitar)?\s*", re.IGNORECASE)

# Continuacoes que sao notas (vao para 'notas', nao para condicao/mensagem)
PAT_NOTA = re.compile(
    r"^\s*(Exce[cç][aã]o|Observa[cç][aã]o|IMPORTANTE|Nota|Criterio|Aten[cç][aã]o)\b",
    re.IGNORECASE,
)


def _parece_linha_tabela(texto):
    """Verifica se a linha parece uma linha de tabela achatada (nao um titulo)."""
    return bool(PAT_ROW_SHAPE.search(texto))


def _detectar_titulo(linha, em_tabela, permitir_numero_ponto=False):
    """
    Detecta se a linha e um titulo de secao.

    Returns:
        tuple (numero, titulo) ou (None, None)
    """
    texto = linha.strip()
    if not texto or ".." in texto:
        return None, None

    # Uma regra de validacao nunca e titulo (ex: "01 A tag... Obrig. 365 Rej.")
    if parse_regra(texto) is not None:
        return None, None

    # Dentro de tabela o titulo top-level so quebra se nao for linha de tabela
    m = PAT_SUB.match(texto)
    if m:
        numero, titulo = m.group(1), m.group(2).strip()
        if len(titulo) < 3 or _parece_linha_tabela(texto):
            return None, None
        # Linha de leiaute de MOC formato NF-e (ex: "245.17 N10b ... CG N01 1-1")
        if PAT_MOC_ROW.search(texto):
            return None, None
        # Numero iniciando com ano (ex: "2025.002 divulga...") nao e secao
        if len(numero.split(".")[0]) == 4:
            return None, None
        # Linha de tabela de historico: "1.10 Setembro/2026 Alteracao em..."
        if re.match(r"^[A-Z][a-zç]+/\d{4}", titulo):
            return None, None
        return numero, titulo

    m = PAT_TOP.match(texto)
    if m:
        numero, titulo = m.group(1), m.group(2).strip()
        if len(titulo) < 3:
            return None, None
        if PAT_TAG_PREFIX.match(titulo):
            return None, None
        if _parece_linha_tabela(texto):
            return None, None
        # Linha de leiaute de MOC (ex: "7 CFOP 2 ... E C 1 - 1 4 ER51")
        if PAT_MOC_ROW.search(texto):
            return None, None
        return numero, titulo

    if permitir_numero_ponto:
        m = PAT_SUB_COM_PONTO.match(texto)
        if not m:
            m = PAT_TOP_COM_PONTO.match(texto)
        if m and not (m.group(1).count(".") >= 1 and len(m.group(1).split(".")[0]) == 4):
            numero, titulo = m.group(1), m.group(2).strip()
            if len(titulo) < 3:
                m = None
            elif _parece_linha_tabela(texto):
                m = None
            elif PAT_MOC_ROW.search(texto):
                m = None
            # "N. Item de lista/procedimento" (ex: "1. Campo C17 - ..."): nao e secao
            elif PAT_NUMERO_PONTO_LISTA.match(titulo):
                m = None
            else:
                return numero, titulo

    return None, None


def _detectar_header(texto, em_tabela):
    """
    Verifica se a linha e cabecalho de tabela.

    Em texto: qualquer linha "# ..." inicia tabela.
    Em tabela: um "# ..." que CONTINUA cabecalho (repetido na pagina
    seguinte) e ignorado; um "# ..." diferente (linha de grupo) e dado.
    """
    m = PAT_HEADER.match(texto.strip())
    if not m:
        return False, None
    corpo = m.group(1)
    eh_header = bool(
        re.match(r"^(ID|Campo|Modelo)\b", corpo)
        or re.search(r"Regra[s]? de Valida", corpo, re.IGNORECASE)
    )
    if not em_tabela:
        return True, corpo  # qualquer "# ..." fora de tabela inicia tabela
    # Em tabela: so e cabecalho se for repeticao de cabecalho
    return eh_header, corpo


def _tipo_header(texto):
    """Determina se o cabecalho e de regras ou de leiaute."""
    if re.search(r"Regra[s]? de Valida", texto, re.IGNORECASE):
        return "regras"
    return "tabela"


def parse_regra(linha):
    """
    Faz parse de uma linha achatada de regra de validacao.

    Ex: "002 Se CST do IBS/CBS for informado... Obrig. 311 Rej. Rejeição: CST..."

    Returns:
        dict com id, modelo, aplicacao, cStat, efeito, condicao, mensagem
        ou None se nao for regra.
    """
    texto = linha.strip().replace("•", " ")
    m = PAT_REGRA_INICIO.match(texto)
    if not m:
        return None
    regra_id = m.group(1)
    resto = m.group(2)

    modelo = ""
    m2 = PAT_MODELO.match(resto)
    if m2:
        modelo = m2.group(1)
        resto = m2.group(2)

    m3 = PAT_APLICACAO.search(resto)
    if not m3:
        return None
    aplicacao = m3.group(1).rstrip(".")
    condicao = resto[: m3.start()].strip()
    cauda = resto[m3.end() :]

    m4 = PAT_CSTAT.search(cauda)
    cstat = m4.group(1) if m4 else ""
    depois = cauda[m4.end() :] if m4 else cauda

    m5 = PAT_EFEITO.match(depois)
    efeito = (m5.group(1) or "").rstrip(".")
    mensagem = depois[m5.end() :].strip()

    return {
        "id": regra_id,
        "modelo": modelo,
        "aplicacao": aplicacao,
        "cStat": cstat,
        "efeito": efeito,
        "condicao": condicao,
        "mensagem": mensagem,
    }


def _eh_nova_regra(linha):
    """Uma linha inicia nova regra se tem id + aplicacao + cStat."""
    r = parse_regra(linha)
    if r is None:
        return None
    if not r["cStat"]:
        return None
    return r


def parse_linha_tabela(linha, cabecalho):
    """
    Faz parse de uma linha achatada de tabela de leiaute.

    Ex: "46 C17 IE Inscrição Estadual do Emitente E C01 C 0-1 2-14 Informar..."
        "1 CST E IBSCBS N 1-1 3 Código da Situação Tributária..."

    Returns:
        dict com campos estruturados + 'texto' original
    """
    texto = linha.strip()
    resultado = {"texto": texto}

    # Linha de grupo: "# IBSCBS G imp - 0-1 - Grupo..."
    eh_grupo = False
    if texto.startswith("# "):
        eh_grupo = True
        texto = texto[2:].strip()
        resultado["texto"] = linha.strip()

    # Tentar match completo: pre + ele + pai + tipo + ocor + tam + obs
    m = re.match(
        r"^(?P<pre>.*?)\s+(?P<ele>[EG])\s+(?P<pai>\S+)\s+"
        r"(?P<tipo>[\w.()-]+)\s+(?P<ocor>\d+-\d+)\s+(?P<tam>[\d.,/-]+)\s*(?P<obs>.*)$",
        texto,
    )
    if m:
        resultado.update(
            {
                "ele": m.group("ele"),
                "pai": m.group("pai"),
                "tipo": m.group("tipo"),
                "ocorrencia": m.group("ocor"),
                "tamanho": m.group("tam"),
                "descricao": "",
                "observacao": m.group("obs").strip(),
            }
        )
        _preencher_pre(resultado, m.group("pre"), eh_grupo)
        return resultado

    # Fallback sem tipo/tam: pre + ele + pai + ocor + obs
    m = re.match(
        r"^(?P<pre>.*?)\s+(?P<ele>[EG])\s+(?P<pai>\S+)\s+"
        r"(?P<ocor>\d+-\d+)\s*(?P<obs>.*)$",
        texto,
    )
    if m:
        resultado.update(
            {
                "ele": m.group("ele"),
                "pai": m.group("pai"),
                "tipo": "",
                "ocorrencia": m.group("ocor"),
                "tamanho": "",
                "descricao": "",
                "observacao": m.group("obs").strip(),
            }
        )
        _preencher_pre(resultado, m.group("pre"), eh_grupo)
        return resultado

    return None


def _preencher_pre(resultado, pre, eh_grupo):
    """Divide o prefixo da linha em num/campo/descricao."""
    pre = pre.strip()
    if eh_grupo:
        resultado["num"] = "#"
        partes = pre.split(None, 1)
        resultado["campo"] = partes[0] if partes else ""
        resultado["descricao"] = partes[1] if len(partes) > 1 else ""
        return
    partes = pre.split(None, 2)
    if len(partes) >= 2:
        resultado["num"] = partes[0]
        resultado["campo"] = partes[1]
        resultado["descricao"] = partes[2] if len(partes) > 2 else ""
    else:
        resultado["num"] = ""
        resultado["campo"] = partes[0] if partes else ""
        resultado["descricao"] = ""


def _marcacao_dominante(marcacoes):
    """Retorna a marcacao mais relevante (EXCLUIDO > AMARELO > VERDE > ...)."""
    prioridade = ["EXCLUIDO", "AMARELO", "VERDE"]
    for p in prioridade:
        if p in marcacoes:
            return p
    for m in marcacoes:
        if m != "SEM_MARCA":
            return m
    return "SEM_MARCA"


def _montar_paragrafos(linhas):
    """
    Agrupa linhas de texto corrido em paragrafos.

    Junta linhas quebradas enquanto terminarem sem pontuacao final
    e mantiverem a mesma marcacao.

    Returns:
        lista de dicts {texto, marcacao, pagina}
    """
    paragrafos = []
    atual_texto = []
    atual_marc = []
    atual_pagina = None

    def fechar():
        nonlocal atual_texto, atual_marc, atual_pagina
        if atual_texto:
            paragrafos.append(
                {
                    "texto": " ".join(atual_texto),
                    "marcacao": _marcacao_dominante(atual_marc),
                    "pagina": atual_pagina,
                }
            )
        atual_texto = []
        atual_marc = []
        atual_pagina = None

    for linha in linhas:
        texto = linha["text"].strip()
        marc = linha.get("marcacao", "SEM_MARCA")
        pagina = linha.get("pagina")

        if not texto:
            continue

        comeca_com_bullet = bool(re.match(r"^([•▪*-]|\d{1,2}[.)])\s", texto))
        anterior_fechou = bool(
            atual_texto and re.search(r"[.!?:;]$", atual_texto[-1])
        )
        mesma_marcacao = not atual_marc or marc == atual_marc[0]

        if atual_texto and (comeca_com_bullet or anterior_fechou or not mesma_marcacao):
            fechar()

        if not atual_texto:
            atual_pagina = pagina
        atual_texto.append(texto)
        atual_marc.append(marc)

    fechar()
    return paragrafos


def montar_secoes_typed(linhas, logger=None):
    """
    Converte lista de linhas (com marcacao e pagina) em secoes tipificadas.

    Args:
        linhas: lista de dicts {text, marcacao, pagina}
        logger: logger opcional

    Returns:
        lista de secoes: {numero, titulo, tipo, cabecalho?, linhas?/regras?/paragrafos?}
    """
    # Expandir textos com quebras internas
    expandidas = []
    for item in linhas:
        texto = item.get("text", "")
        partes = texto.split("\n") if "\n" in texto else [texto]
        for p in partes:
            if p.strip():
                expandidas.append(
                    {
                        "text": p.strip(),
                        "marcacao": item.get("marcacao", "SEM_MARCA"),
                        "pagina": item.get("pagina"),
                    }
                )

    secoes = []
    numero, titulo = "0", "Geral"

    # Estado do bloco corrente
    modo = "texto"  # "texto" | "tabela"
    tipo_tabela = None  # "regras" | "tabela"
    cabecalho = []
    paragrafos = []  # acumulador de linhas de texto
    regras = []  # acumulador de regras
    linhas_tabela = []  # acumulador de linhas de tabela
    linhas_avulsas = []  # linhas em tabela de regras antes da primeira regra
    grupo_atual = ""  # rotulo de grupo em tabelas de regras

    def fechar_secao():
        nonlocal paragrafos, regras, linhas_tabela, linhas_avulsas
        nonlocal tipo_tabela, cabecalho, grupo_atual
        if modo == "texto" and paragrafos:
            secoes.append(
                {
                    "numero": numero,
                    "titulo": titulo,
                    "tipo": "texto",
                    "paragrafos": _montar_paragrafos(paragrafos),
                }
            )
        elif modo == "tabela":
            if tipo_tabela == "regras" and regras:
                secoes.append(
                    {
                        "numero": numero,
                        "titulo": titulo,
                        "tipo": "regras",
                        "regras": regras,
                    }
                )
            elif tipo_tabela == "regras" and linhas_avulsas:
                # Fallback: nenhuma regra reconhecida -> texto corrido
                secoes.append(
                    {
                        "numero": numero,
                        "titulo": titulo,
                        "tipo": "texto",
                        "paragrafos": _montar_paragrafos(linhas_avulsas),
                    }
                )
            elif tipo_tabela == "tabela" and linhas_tabela:
                secoes.append(
                    {
                        "numero": numero,
                        "titulo": titulo,
                        "tipo": "tabela",
                        "cabecalho": cabecalho,
                        "linhas": linhas_tabela,
                    }
                )
        paragrafos = []
        regras = []
        linhas_tabela = []
        linhas_avulsas = []
        tipo_tabela = None
        cabecalho = []
        grupo_atual = ""

    def iniciar_tabela(header_texto):
        nonlocal modo, tipo_tabela, cabecalho, paragrafos
        # Fechar texto pendente antes de virar tabela
        if paragrafos:
            secoes.append(
                {
                    "numero": numero,
                    "titulo": titulo,
                    "tipo": "texto",
                    "paragrafos": _montar_paragrafos(paragrafos),
                }
            )
            paragrafos = []
        modo = "tabela"
        tipo_tabela = _tipo_header(header_texto)
        m = PAT_HEADER.match(header_texto.strip())
        cabecalho = m.group(1).split() if m else []

    def voltar_texto():
        """Tabela invalida volta para modo texto."""
        nonlocal modo, tipo_tabela, cabecalho
        modo = "texto"
        tipo_tabela = None
        cabecalho = []

    for item in expandidas:
        texto = item["text"]
        marc = item.get("marcacao", "SEM_MARCA")
        pagina = item.get("pagina")

        # 1. Titulo de secao?
        novo_num, novo_titulo = _detectar_titulo(texto, modo == "tabela")
        if novo_num is not None:
            fechar_secao()
            numero, titulo = novo_num, novo_titulo
            modo = "texto"
            continue

        # 2. Cabecalho de tabela?
        eh_header, _ = _detectar_header(texto, modo == "tabela")
        if eh_header:
            if modo == "tabela":
                # Cabecalho repetido na pagina seguinte da mesma tabela
                if _tipo_header(texto) == tipo_tabela:
                    continue
                # Mudanca de tipo de tabela: fechar a atual e abrir outra
                fechar_secao()
                iniciar_tabela(texto)
                continue
            iniciar_tabela(texto)
            continue

        if modo == "texto":
            paragrafos.append(item)
            continue

        # --- Dentro de tabela ---
        if PAT_ELLIPSIS.match(texto):
            continue

        if tipo_tabela == "regras":
            nova = _eh_nova_regra(texto)
            if nova:
                nova["marcacao"] = marc
                nova["pagina"] = pagina
                nova["grupo"] = grupo_atual
                nova["notas"] = []
                nova["texto_completo"] = texto
                regras.append(nova)
            elif regras:
                r = regras[-1]
                r["notas"].append({"texto": texto, "marcacao": marc})
                r["texto_completo"] += "\n" + texto
            else:
                # Linha antes da primeira regra: rotulo de grupo / texto
                if not grupo_atual:
                    grupo_atual = texto
                linhas_avulsas.append(item)
        else:
            linha_parse = parse_linha_tabela(texto, cabecalho)
            if linha_parse:
                linha_parse["marcacao"] = marc
                linha_parse["pagina"] = pagina
                linhas_tabela.append(linha_parse)
            elif linhas_tabela:
                # Continuacao da linha anterior (quebra de celula)
                anterior = linhas_tabela[-1]
                anterior["texto"] += " " + texto
                anterior["observacao"] = (
                    anterior.get("observacao", "") + " " + texto
                ).strip()
            elif re.match(r"^#", texto):
                # Outro "# ..." apos invalidacao: novo cabecalho
                voltar_texto()
                iniciar_tabela(texto)
            else:
                # Linha que nao parece tabela: voltar para texto
                paragrafos.append(item)
                voltar_texto()

    fechar_secao()

    if logger:
        tipos = {}
        for s in secoes:
            tipos[s["tipo"]] = tipos.get(s["tipo"], 0) + 1
        logger.info(f"Secoes tipificadas: {len(secoes)} ({tipos})")

    return secoes


def calcular_estatisticas(secoes):
    """
    Calcula estatisticas das secoes tipificadas.

    Returns:
        dict com total_secoes, total_regras, total_tabelas, por_marcacao
    """
    por_marcacao = {"AMARELO": 0, "VERDE": 0, "EXCLUIDO": 0, "SEM_MARCA": 0}
    total_regras = 0
    total_tabelas = 0

    def contabilizar(marc):
        if marc in por_marcacao:
            por_marcacao[marc] += 1
        else:
            por_marcacao["SEM_MARCA"] += 1

    for s in secoes:
        if s["tipo"] == "texto":
            for p in s.get("paragrafos", []):
                contabilizar(p.get("marcacao", "SEM_MARCA"))
        elif s["tipo"] == "regras":
            total_tabelas += 1
            for r in s.get("regras", []):
                total_regras += 1
                contabilizar(r.get("marcacao", "SEM_MARCA"))
                for n in r.get("notas", []):
                    contabilizar(n.get("marcacao", "SEM_MARCA"))
        elif s["tipo"] == "tabela":
            total_tabelas += 1
            for ln in s.get("linhas", []):
                contabilizar(ln.get("marcacao", "SEM_MARCA"))

    return {
        "total_secoes": len(secoes),
        "total_regras": total_regras,
        "total_tabelas": total_tabelas,
        "por_marcacao": por_marcacao,
    }
