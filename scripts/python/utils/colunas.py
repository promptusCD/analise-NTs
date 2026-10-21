"""
utils/colunas.py - Leitura de tabelas por coluna, usando a posicao (x, y) dos spans.

Por que: juntar texto por posicao vertical mistura as colunas de uma tabela (a
continuacao da mensagem de uma regra cai nas notas da coluna ao lado). Aqui cada
span e atribuido a uma coluna pelo centro do seu bbox, e as colunas sao
derivadas do CABECALHO da tabela.

Entrada: lista de "spans" no formato de utils/cores.py::extract_page_content
(dict com 'text', 'bbox' [x0, y0, x1, y1], 'size', 'marcacao', ...).
Todas as funcoes sao puras (sem I/O) para serem testadas com spans sinteticos.
"""

import logging
import re

LOG = logging.getLogger(__name__)

# Versao na coluna "Versao": "1.00", "1.10a", "1.12 a" (o espaco e removido depois)
PAT_VERSAO = re.compile(r"^\d+\.\d+(?:\s?[a-z])?$")
# Marcadores de "sem data" nas celulas de implantacao
PLACEHOLDERS = {"", "-", "-x-", "–", "—", "x"}
# Glifos de lista (bullets) que nao fazem parte do texto
BULLETS = {"", "•", "▪", "·", "*"}

TOLERANCIA_COLUNA_VERSAO = 30
TOLERANCIA_COLUNA_DATA = 40
FOLGA_INICIO_LINHA = 8  # a 1a linha de texto de uma linha da tabela pode ficar acima do y da versao
MARGEM_SUPERIOR_CONTINUACAO = 60  # abaixo do cabecalho corrente da pagina
TAMANHO_TITULO = 12.5  # spans maiores que isso sao titulos de secao


def _x0(s):
    return s["bbox"][0]


def _x1(s):
    return s["bbox"][2]


def _y(s):
    return s["bbox"][1]


def _cx(s):
    return (s["bbox"][0] + s["bbox"][2]) / 2.0


def _texto(s):
    return re.sub(r"\s+", " ", s["text"]).strip()


def normalizar_celula(texto):
    """Texto de celula de implantacao: espacos colapsados; marcadores de ausencia viram ''."""
    t = re.sub(r"\s+", " ", texto or "").strip()
    return "" if t.lower() in PLACEHOLDERS else t


def achar_cabecalho_cronograma(spans):
    """
    Localiza o cabecalho da tabela de cronograma ('Versao | Historico de atualizacoes |
    Implantacao ... | Implantacao ...') e devolve a geometria das colunas.

    Returns:
        dict {y, versao_cx, data_cx: [homologacao, producao]} ou None
    """
    for h in (s for s in spans if re.search(r"hist.rico de atualiza", s["text"], re.IGNORECASE)):
        y = _y(h)
        mesma_linha = [s for s in spans if abs(_y(s) - y) <= 3]
        versao = [s for s in mesma_linha if re.fullmatch(r"vers.o", _texto(s), re.IGNORECASE)]
        implantacao = sorted(
            (s for s in mesma_linha if re.search(r"implanta", s["text"], re.IGNORECASE)), key=_cx
        )
        if versao and len(implantacao) >= 2:
            return {
                "y": y,
                "versao_cx": _cx(versao[0]),
                "data_cx": [_cx(implantacao[0]), _cx(implantacao[1])],
            }
    return None


def _marcador_de_fim(spans, y_min):
    """y do primeiro span (abaixo de y_min) que encerra a tabela: 'Observacao...' ou titulo grande."""
    candidatos = [
        _y(s)
        for s in spans
        if _y(s) > y_min and (_texto(s).lower().startswith("observa") or s.get("size", 0) >= TAMANHO_TITULO)
    ]
    return min(candidatos) if candidatos else float("inf")


def _tokens_de_versao(spans, geo, y_min, y_max):
    toks = [
        s
        for s in spans
        if y_min < _y(s) < y_max
        and PAT_VERSAO.match(_texto(s))
        and abs(_cx(s) - geo["versao_cx"]) <= TOLERANCIA_COLUNA_VERSAO
    ]
    return sorted(toks, key=_y)


def _linhas_da_pagina(spans, geo, y_min, continuacao, descartar_ate_y=0.0):
    """
    Divide uma pagina da tabela em linhas (uma por token de versao).

    Returns:
        (linhas, sobra) - linhas: [{'versao', 'spans', 'y0', 'y1'}]; sobra: spans que ficaram
        ANTES do primeiro token (continuacao da ultima linha da pagina anterior)
    """
    fim = _marcador_de_fim(spans, y_min)
    toks = _tokens_de_versao(spans, geo, y_min, fim)
    if not toks:
        return [], []
    limites = [_y(t) - FOLGA_INICIO_LINHA for t in toks] + [fim]
    # Rodape "Pagina N / M": tudo a partir dele (inclusive seus numeros) fica fora da tabela
    rodape = [_y(s) for s in spans if re.match(r"^P.gina\b", _texto(s)) and _y(s) > y_min]
    corte = (min(rodape) - 2) if rodape else float("inf")
    area = [s for s in spans if y_min < _y(s) < min(fim, corte) and _y(s) > descartar_ate_y]
    linhas = []
    for i, t in enumerate(toks):
        a, b = limites[i], limites[i + 1]
        linhas.append(
            {"versao": re.sub(r"\s+", "", _texto(t)), "spans": [s for s in area if a <= _y(s) < b], "y0": a, "y1": b}
        )
    sobra = [s for s in area if _y(s) < limites[0]] if continuacao else []
    return linhas, sobra


def _montar_entrada(linha, geo):
    """Constroi {'versao','homologacao','producao','descricao'} de uma linha, ou None se sem datas."""
    centro_desc_max = geo["data_cx"][0] - 25
    centro_desc_min = geo["versao_cx"] + 25

    def celula(i):
        spans = [
            s
            for s in linha["spans"]
            if abs(_cx(s) - geo["data_cx"][i]) <= TOLERANCIA_COLUNA_DATA and _texto(s) not in BULLETS
        ]
        spans.sort(key=lambda s: (round(_y(s) / 3), _x0(s)))
        return normalizar_celula(" ".join(_texto(s) for s in spans))

    homologacao, producao = celula(0), celula(1)
    if not homologacao and not producao:
        return None

    desc_spans = [
        s
        for s in linha["spans"]
        if centro_desc_min < _cx(s) < centro_desc_max and _texto(s) not in BULLETS
    ]
    desc_spans.sort(key=lambda s: (round(_y(s) / 3), _x0(s)))
    descricao = re.sub(r"\s+", " ", " ".join(_texto(s) for s in desc_spans)).strip()

    return {
        "versao": linha["versao"],
        "homologacao": homologacao,
        "producao": producao,
        "descricao": descricao,
    }


def extrair_cronograma_tabela(paginas, max_paginas=8):
    """
    Le a tabela 'Historico de Alteracoes / Cronograma' de uma NT, por coluna.

    Args:
        paginas: lista (uma por pagina) de listas de spans (ver topo do modulo)
        max_paginas: procura o cabecalho so nas primeiras paginas

    Returns:
        lista de {'versao', 'homologacao', 'producao', 'descricao'} na ordem do documento;
        [] se a tabela nao for reconhecida. Versoes sem nenhuma data nao geram entrada.
    """
    geo = None
    inicio = None
    for i, spans in enumerate(paginas[:max_paginas]):
        geo = achar_cabecalho_cronograma(spans)
        if geo:
            inicio = i
            break
    if geo is None:
        return []

    todas_linhas = []
    for i in range(inicio, len(paginas)):
        spans = paginas[i]
        continuacao = i > inicio
        y_min = MARGEM_SUPERIOR_CONTINUACAO if continuacao else geo["y"] + 15
        linhas, sobra = _linhas_da_pagina(spans, geo, y_min, continuacao)

        if continuacao:
            primeira = [s for s in spans if _y(s) > y_min]
            # So continua se a primeira coisa da pagina, abaixo do cabecalho corrente, for uma versao
            if not linhas or not primeira:
                break
            y_topo = min(_y(s) for s in primeira)
            topo = [s for s in primeira if _y(s) <= y_topo + 3]  # marcador de lista pode empatar com a versao
            if not any(
                PAT_VERSAO.match(_texto(s)) and abs(_cx(s) - geo["versao_cx"]) <= TOLERANCIA_COLUNA_VERSAO
                for s in topo
            ):
                break
            if sobra and todas_linhas:
                todas_linhas[-1]["spans"].extend(sobra)

        if not linhas:
            break
        todas_linhas.extend(linhas)

        # A tabela terminou nesta pagina se houve marcador de fim (Observacao/titulo) apos a ultima versao
        if _marcador_de_fim(spans, y_min) != float("inf"):
            break

    entradas = [e for e in (_montar_entrada(l, geo) for l in todas_linhas) if e]
    return entradas


# ---------------------------------------------------------------------------
# Tabelas de regras de validacao: linearizacao por coluna
# ---------------------------------------------------------------------------
# Colunas de uma tabela de regras (NF-e/CT-e/MDF-e):
#   [#/ID] [Modelo] [Regra de Validacao ...] | [Aplic.] [Msg/cStat] [Efeito] [Mensagem ...]
# A coluna "Regra" (esquerda) tem condicao e notas; as colunas Aplic./cStat/Efeito/Mensagem
# (direita) tem a mensagem, que pode quebrar em varias linhas. Juntar tudo por y mistura as duas.
# A fronteira entre os dois lados e o x da coluna "Aplic.", aprendido do proprio documento.
# Token de aplicacao no inicio do span: 'Obrig.', 'Obrig' / 'Obrig,' (typo do PDF na regra 1063), 'Facult.',
# 'Facul.' (K01-10), 'Futura'... O \b rejeita 'Obrigatorio' (que aparece no texto das regras).
PAT_APLICACAO = re.compile(r"^(Obrig|Facult?|Facultativ[ao]|Futura|Opcional)\b", re.IGNORECASE)
# Inicio de LINHA DE REGRA: aplicacao SEGUIDA do cStat. So a palavra nao basta: 'opcional.' e 'Futura' aparecem
# no texto da coluna Observacao das tabelas de leiaute dos MOCs (e nao sao linhas de regra).
PAT_INICIO_REGRA = re.compile(
    r"^(Obrig|Facult?|Facultativ[ao]|Futura|Opcional)[.,]?\s+\d{3,4}\b", re.IGNORECASE
)
PAT_RODAPE = re.compile(r"^P.gina\s+\d+\s*/\s*\d+$")
PONTUACAO_SOLTA = {".", ","}  # span so com isso, em linha de continuacao da direita, nao e mensagem
TOLERANCIA_MENSAGEM = 6  # continuacao de mensagem comeca na mesma coluna (ou a direita) do inicio da mensagem
FRACAO_MIN_FRONTEIRA = 0.30  # a coluna Aplic. nunca esta no primeiro terco da pagina
MARGEM_FRONTEIRA = 6
TOLERANCIA_LINHA = 3.0
ALTURA_MIN_TITULO = 11.0  # texto de tabela tem <= 9 pt; titulos de secao >= 11 pt
Y_TOPO_PAGINA = 80  # linhas acima disso sao candidatas a cabecalho corrente (se repetirem na pagina anterior)
Y_CABECALHO_CERTO = 50  # acima disso e sempre cabecalho corrente


def agrupar_em_linhas(spans, tolerancia=TOLERANCIA_LINHA):
    """Agrupa spans em linhas por posicao vertical (mesma regra de cores.aggregate_spans_into_lines)."""
    ordenados = sorted(spans, key=lambda s: (_y(s), _x0(s)))
    linhas, atual, y_atual = [], [], None
    for s in ordenados:
        if y_atual is None or abs(_y(s) - y_atual) > tolerancia:
            if atual:
                linhas.append(sorted(atual, key=_x0))
            atual, y_atual = [s], _y(s)
        else:
            atual.append(s)
    if atual:
        linhas.append(sorted(atual, key=_x0))
    return linhas


def detectar_fronteira_direita(spans, largura=None):
    """
    x a partir do qual comecam as colunas Aplic./cStat/Efeito/Mensagem, ou None se a pagina nao
    tem linhas de regra. Aprende dos spans que comecam por 'Obrig.'/'Facult.'/'Futura'.
    """
    xs = []
    for linha in agrupar_em_linhas(spans):
        for k, s in enumerate(linha):
            if not PAT_APLICACAO.match(_texto(s)):
                continue
            if largura is not None and _x0(s) < FRACAO_MIN_FRONTEIRA * largura:
                continue
            if PAT_INICIO_REGRA.match(" ".join(_texto(t) for t in linha[k:])):  # aplicacao + cStat
                xs.append(_x0(s))
            break  # so o 1o token de aplicacao da linha conta
    xs.sort()
    if not xs:
        return None
    mediana = xs[len(xs) // 2]
    proximos = [x for x in xs if abs(x - mediana) <= 25]  # ignora ocorrencias soltas no texto
    return min(proximos) - MARGEM_FRONTEIRA


def _texto_linha(linha):
    return " ".join(_texto(s) for s in linha if _texto(s))


# Aplicacao no FIM do texto da esquerda: em algumas tabelas do MOC o 'Facul.'/'Obrig.' vem DENTRO do span
# longo da coluna Regra (que invade a coluna Aplic.), e so o cStat fica na direita.
PAT_APLICACAO_NO_FIM = re.compile(r"\b(Obrig|Facult?|Facultativ[ao]|Futura|Opcional)[.,]?$", re.IGNORECASE)


def _eh_inicio_de_regra(esquerda, direita):
    """Primeira linha de uma regra: (aplicacao + cStat) a direita, ou aplicacao no fim da esquerda + cStat."""
    txt_dir = " ".join(_texto(s) for s in direita)
    if PAT_INICIO_REGRA.match(txt_dir):
        return True
    txt_esq = " ".join(_texto(s) for s in esquerda)
    return bool(PAT_APLICACAO_NO_FIM.search(txt_esq) and re.match(r"^\d{3,4}\b", txt_dir))


def _eh_titulo(linha):
    return max(s.get("size", 0) for s in linha) >= ALTURA_MIN_TITULO


def _eh_cabecalho_regras(linha):
    t = _texto_linha(linha)
    return bool(re.search(r"Regra\s+de\s+Valida", t, re.IGNORECASE) and re.search(r"Aplic", t, re.IGNORECASE))


def _item(spans, texto=None, **extra):
    """Item de linha no formato de cores._merge_line (text, marcacao, trechos, bbox, size, bold)."""
    from utils.cores import marcacao_dominante, trechos_de_spans

    spans = sorted(spans, key=lambda s: (round(_y(s) / TOLERANCIA_LINHA), _x0(s)))
    trechos = trechos_de_spans(spans)
    x0 = min(s["bbox"][0] for s in spans)
    y0 = min(s["bbox"][1] for s in spans)
    x1 = max(s["bbox"][2] for s in spans)
    y1 = max(s["bbox"][3] for s in spans)
    item = {
        "text": texto if texto is not None else " ".join(t["texto"] for t in trechos),
        "marcacao": marcacao_dominante(t["marcacao"] for t in trechos),
        "trechos": trechos,
        "bold": any(s.get("bold") for s in spans),
        "size": max(s.get("size", 0) for s in spans),
        "bbox": [x0, y0, x1, y1],
        "line_y": (y0 + y1) / 2,
    }
    item.update(extra)
    return item


def linearizar_pagina(spans, largura=None, estado=None):
    """
    Converte os spans de uma pagina em itens de linha, separando as colunas das tabelas de regras.

    Linhas fora de tabelas de regra ficam como antes (juntas por y). Em tabela de regras:
      - 1 item canonico por regra: '<esquerda da 1a linha> <todo o texto das colunas da direita>'
        (id, modelo, condicao, Aplic., cStat, Efeito e a MENSAGEM COMPLETA);
      - 1 item por linha de continuacao da coluna esquerda (notas: Excecao/Observacao/itens);
      - linhas so-da-direita no topo da pagina (regra iniciada na pagina anterior) viram itens
        com continuacao_mensagem=True.
      - cabecalhos 'Campo | Modelo | Regra de Validacao | Aplic. ...' sem '#' ganham o prefixo '# '.

    Args:
        spans: spans da pagina (cores.extract_page_content)
        largura: largura da pagina (pt), para ignorar 'Obrig.' fora de lugar
        estado: dict mutavel compartilhado entre paginas ({'fx', 'em_regra'})

    Returns:
        lista de itens ordenada por posicao vertical
    """
    from utils.cores import _merge_line

    if estado is None:
        estado = {}
    fx = detectar_fronteira_direita(spans, largura)
    if fx is not None:
        estado["fx"] = fx
    fx = fx if fx is not None else estado.get("fx")
    em_regra = estado.get("em_regra", False)

    itens = []
    regra = None  # {'esq': spans da 1a linha, 'dir': spans, 'cont': [[spans esquerda]...]}

    def fechar():
        nonlocal regra
        if regra is None:
            return
        estado["msg_x0"] = regra["msg_x0"]  # para validar continuacoes no topo da pagina seguinte
        esq = regra["esq"]
        direita = sorted(regra["dir"], key=lambda s: (round(_y(s) / TOLERANCIA_LINHA), _x0(s)))
        todos = esq + direita
        texto = " ".join(_texto(s) for s in esq + direita if _texto(s))
        itens.append(_item(todos, texto=texto))
        for cont in regra["cont"]:
            itens.append(_item(cont))
        regra = None

    topo_anterior = estado.get("topo_anterior", set())
    topo_atual = set()
    cabecalho_emitido = estado.get("cabecalho_emitido", False)

    for linha in agrupar_em_linhas(spans):
        y = _y(linha[0])
        texto_linha = _texto_linha(linha)
        if y < Y_TOPO_PAGINA:
            topo_atual.add((texto_linha, round(y)))

        # Cabecalho corrente (igual ao da pagina anterior, ou no alto da pagina) e rodape: ficam como
        # linhas normais e NAO encerram a regra (a regra pode continuar na pagina seguinte)
        eh_cabecalho_pagina = (texto_linha, round(y)) in topo_anterior or y < Y_CABECALHO_CERTO
        if PAT_RODAPE.match(texto_linha) or eh_cabecalho_pagina:
            fechar()
            itens.append(_merge_line(linha))
            continue

        # Titulos e cabecalhos de tabela encerram a regra corrente
        if _eh_titulo(linha) or _eh_cabecalho_regras(linha):
            fechar()
            em_regra = False
            cabecalho_emitido = _eh_cabecalho_regras(linha)  # titulo: a proxima tabela precisa de cabecalho
            if _eh_cabecalho_regras(linha) and not texto_linha.startswith("#"):
                itens.append(_item(linha, texto="# " + texto_linha))
            else:
                item = _merge_line(linha)
                if _eh_titulo(linha):
                    # Titulo por tamanho de fonte (>= 11 pt; texto de tabela tem <= 9): o MOC aceita numeracao
                    # "N." / "N.N." mesmo dentro de uma regiao de tabela quando a fonte e de titulo
                    item["eh_titulo"] = True
                itens.append(item)
            continue

        # Outro cabecalho de tabela ('# Campo Ele Pai ...'): a proxima tabela de regras precisa do seu
        if texto_linha.startswith("#"):
            fechar()
            em_regra = False
            cabecalho_emitido = False
            itens.append(_merge_line(linha))
            continue

        if fx is None:
            itens.append(_merge_line(linha))
            continue

        esquerda = [s for s in linha if _x0(s) < fx]
        direita = [s for s in linha if _x0(s) >= fx]

        if direita and _eh_inicio_de_regra(esquerda, direita):  # 1a linha de uma regra
            fechar()
            if not cabecalho_emitido:
                # Tabela de regras sem linha de cabecalho (MDF-e; CT-e 'Validacoes dos Documentos
                # Transportados'): sem ele o classificador nunca entra em modo 'regras'
                itens.append(_cabecalho_sintetico(linha))
                cabecalho_emitido = True
            # msg_x0: onde a mensagem comeca (maior x da PRIMEIRA linha da direita), p/ distinguir o
            # ponto sobrante da coluna Efeito do ponto final da mensagem
            regra = {"esq": esquerda, "dir": list(direita), "cont": [], "msg_x0": max(_x0(s) for s in direita)}
            em_regra = True
        elif em_regra and regra is not None:  # continuacao da regra corrente
            # Um '.' sozinho ABAIXO DA COLUNA EFEITO (a esquerda de onde a mensagem comeca) e o fim de
            # 'Rej.' quebrado em duas linhas; um '.' no fim da mensagem e conteudo e fica
            msg_x0 = regra["msg_x0"]
            util = [s for s in direita if not (_texto(s) in PONTUACAO_SOLTA and _x0(s) < msg_x0 - 3)]
            if any(_x0(s) < msg_x0 - TOLERANCIA_MENSAGEM for s in util):
                # Colunas da direita que NAO sao a da mensagem (ex.: Ele/Pai/Tipo/Ocor de uma tabela de
                # leiaute logo apos a de regras): nao e continuacao, e outra tabela. O cabecalho da tabela
                # de regras continua valendo (o '#' da proxima tabela ou um titulo o reinicia).
                fechar()
                em_regra = False
                itens.append(_merge_line(linha))
                continue
            regra["dir"].extend(util)
            if esquerda:
                regra["cont"].append(esquerda)
        elif em_regra and any(_x0(s) < estado.get("msg_x0", 0) - TOLERANCIA_MENSAGEM for s in direita):
            # topo de pagina com colunas da direita fora da coluna da mensagem: e outra tabela
            em_regra = False
            itens.append(_merge_line(linha))
        elif em_regra:  # topo de pagina: continuacao de uma regra da pagina anterior
            if esquerda:
                itens.append(_item(esquerda))
            if direita:
                itens.append(_item(direita, continuacao_mensagem=True))
        else:
            itens.append(_merge_line(linha))

    fechar()
    estado["em_regra"] = em_regra
    estado["topo_anterior"] = topo_atual
    estado["cabecalho_emitido"] = cabecalho_emitido
    return itens


def _cabecalho_sintetico(linha):
    """Item '# Regra de Validação' (marcado sintetico) para tabela de regras sem cabecalho."""
    y0 = min(s["bbox"][1] for s in linha)
    x0 = min(s["bbox"][0] for s in linha)
    return {
        "text": "# Regra de Validação",
        "marcacao": "SEM_MARCA",
        "trechos": [],
        "bold": False,
        "size": 8.0,
        "bbox": [x0, y0 - 1, x0 + 1, y0],
        "line_y": y0 - 0.5,
        "sintetico": True,
    }
