"""
utils/parsing.py - Parsing de secoes, metadados, cronograma e itens de NTs/MOCs.

Responsabilidades:
- Extrair metadados (nt, versao, documento, titulo) do cabecalho
- Extrair cronograma de vigencia (homologacao/producao)
- Identificar secoes numeradas
- Extrair itens individuais de secoes
- Detectar tipo de documento pelo nome do arquivo
- Calcular SHA256
"""

import re
import hashlib
import logging
from pathlib import Path

LOG = logging.getLogger(__name__)


# Nomenclatura: <DOC>_NT_<numero>_v<versao>.pdf ou CTe_NT_<numero>_v<versao>.pdf
PATTERNS_FILENAME = {
    "NF-e": re.compile(r"NT[_\s](\d{4})[_\s](\d{3})[_\s]v([\d.]+)", re.IGNORECASE),
    "CT-e": re.compile(r"CTe[_\s]NT[_\s](\d{4})[_\s](\d{3})[_\s]v([\d.]+)", re.IGNORECASE),
    "MDF-e": re.compile(r"MDFe[_\s]NT[_\s](\d{4})[_\s](\d{3})[_\s]v([\d.]+)", re.IGNORECASE),
}

# Pattern para MOC: MOC_<DOC>_<secao>_<versao>.pdf
PATTERN_MOC = re.compile(r"MOC[_\s](NFe|CTe|MDFe)[_\s](.+?)[_\s]v([\d.a-z]+)", re.IGNORECASE)

# Pattern para cronograma: datas como DD/MM/YYYY ou "Ate DD/MM/YYYY"
PATTERN_DATA = re.compile(r"(\d{2}/\d{2}/\d{4})")
PATTERN_ATE = re.compile(r"[Aa]t[eé]\s+(\d{2}/\d{2}/\d{4})")

# Pattern para secoes: "1. Titulo" ou "1.1 Titulo" ou "Seção 1"
PATTERN_SECAO = re.compile(r"^(\d+(?:\.\d+)*)\s*[\.\)]\s*(.+)")

# Pattern para IDs de regras: C17-10, 5E17-70, 1051, etc.
PATTERN_REGRA_ID = re.compile(r"([A-Z]?\d[\w-]*\d)")

# Mapeamento de prefixos de arquivo para documento
DOC_PREFIXES = {
    "CTe_": "CT-e",
    "CTe ": "CT-e",
    "MDFe_": "MDF-e",
    "MDFe ": "MDF-e",
    "NT_": "NF-e",
    "NT ": "NF-e",
}


def detect_documento_from_filename(filename):
    """
    Detecta o tipo de documento fiscal pelo nome do arquivo.

    Returns:
        str: "NF-e", "CT-e" ou "MDF-e"
    """
    name = Path(filename).name
    for prefix, doc in DOC_PREFIXES.items():
        if name.startswith(prefix):
            return doc
    # Fallback: tentar por conteudo do nome
    name_upper = name.upper()
    if "CTE" in name_upper or "CT-E" in name_upper:
        return "CT-e"
    if "MDFE" in name_upper or "MDF-E" in name_upper:
        return "MDF-e"
    return "NF-e"


def detect_is_moc(filename):
    """Verifica se o arquivo e um MOC pelo nome."""
    name = Path(filename).name.upper()
    return name.startswith("MOC_")


def calculate_sha256(filepath):
    """
    Calcula o hash SHA256 de um arquivo.

    Returns:
        str: hash hexadecimal
    """
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while True:
            chunk = f.read(8192)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


# Versao no nome do arquivo: "..._v1.14b", "..._v1.00_Valor_Liquido" (sufixo alfabetico faz parte da versao)
PATTERN_VERSAO_NOME = re.compile(r"_v(\d+(?:\.\d+)*[a-z]?)(?=$|[_\s.])", re.IGNORECASE)
PATTERN_NT_NOME = re.compile(r"NT[_\s](\d{4})[_\s](\d{3})", re.IGNORECASE)
# Linha da capa: "Nota Tecnica 2025.001 - Titulo" | "Nota Tecnica 2026.002 Versao 1.11"
PATTERN_CAPA_NT = re.compile(r"^Nota\s+T[eé]cnica\s+(\d{4}\.\d{3})\s*(.*)$", re.IGNORECASE)
PATTERN_CAPA_VERSAO = re.compile(r"^Vers[aã]o\s+(\d+(?:\.\d+)*[a-z]?)\b", re.IGNORECASE)


def parse_titulo_capa(capa_texto):
    """
    Extrai o titulo impresso na capa (pagina 1) de uma NT.

    Layouts conhecidos (as linhas do titulo quebram em 1-2 linhas):
      - CT-e:   "Nota Tecnica N - <titulo>" na mesma linha
      - MDF-e / NF-e (2026.007, 2026.010): titulo entre "Nota Tecnica N" e "Versao ..."
      - NF-e (2026.002, 2026.008): titulo ANTES da linha "Nota Tecnica N ..."
    O nome do projeto ("Projeto ...", quebrado em 2-3 linhas) nunca e titulo.

    Returns:
        str: titulo (linhas unidas por espaco) ou "" se nao identificado
    """
    linhas = [l.strip() for l in capa_texto.splitlines() if l.strip()]
    idx = next((i for i, l in enumerate(linhas) if PATTERN_CAPA_NT.match(l)), None)
    if idx is None:
        return ""

    # 1. Titulo na propria linha: "Nota Tecnica 2025.001 - Reforma Tributaria do Consumo"
    resto = PATTERN_CAPA_NT.match(linhas[idx]).group(2).strip()
    resto = re.sub(r"^[-–—]\s*", "", resto).strip()
    if resto and not re.match(r"^Vers[aã]o\b", resto, re.IGNORECASE):
        return resto

    # 2. Linhas entre "Nota Tecnica N" e "Versao ..."
    depois = []
    for l in linhas[idx + 1:]:
        if PATTERN_CAPA_VERSAO.match(l):
            break
        depois.append(l)
    else:
        depois = []  # sem linha "Versao": nao da para delimitar o titulo
    if depois:
        return " ".join(depois)

    # 3. Linhas antes de "Nota Tecnica N" (sem bloco "Projeto ...")
    antes = linhas[:idx]
    if antes and not antes[0].lower().startswith("projeto"):
        return " ".join(antes)
    return ""


def parse_nt_metadata(page_texts, filename=None):
    """
    Extrai metadados da NT do nome do arquivo e da capa do PDF.

    Args:
        page_texts: lista de textos das paginas (strings)
        filename: nome do arquivo (opcional, para detect_documento)

    Returns:
        dict com 'nt', 'versao', 'documento', 'titulo' e 'avisos' (lista de str)
    """
    metadata = {
        "nt": "",
        "versao": "",
        "documento": "",
        "titulo": "",
        "avisos": [],
    }

    versao_nome = ""
    if filename:
        metadata["documento"] = detect_documento_from_filename(filename)
        name = Path(filename).stem
        m = PATTERN_NT_NOME.search(name)
        if m:
            metadata["nt"] = f"{m.group(1)}.{m.group(2)}"
        m = PATTERN_VERSAO_NOME.search(name)
        if m:
            versao_nome = m.group(1)

    capa = page_texts[0] if page_texts else ""
    primeiras = "\n".join(page_texts[:3])

    # NT: do nome; se faltar, da capa/primeiras paginas
    if not metadata["nt"]:
        m = re.search(r"(?:Nota\s+T[eé]cnica|NT)\s+(\d{4}\.\d{3})", primeiras, re.IGNORECASE)
        if m:
            metadata["nt"] = m.group(1)

    # Versao: do nome (com sufixo alfabetico), conferida com a capa
    versao_capa = ""
    for linha in (l.strip() for l in capa.splitlines()):
        m = PATTERN_CAPA_VERSAO.match(linha) or re.search(r"Vers[aã]o\s+(\d+(?:\.\d+)*[a-z]?)\b", linha, re.IGNORECASE)
        if m:
            versao_capa = m.group(1)
            break
    metadata["versao"] = versao_nome or versao_capa
    if versao_nome and versao_capa and versao_nome.lower() != versao_capa.lower():
        metadata["avisos"].append(
            f"versao do nome do arquivo ({versao_nome}) difere da capa ({versao_capa})"
        )

    metadata["titulo"] = parse_titulo_capa(capa)
    if not metadata["titulo"]:
        metadata["avisos"].append("titulo nao identificado na capa")

    return metadata


def parse_moc_metadata(page_texts, filename=None):
    """
    Extrai metadados do MOC do nome do arquivo (e eventualmente do cabecalho).

    Suporta dois formatos de nome:
      - MOC_CTe_VisaoGeral_v4.00.pdf        (secao antes da versao)
      - MOC_NFe_v7.00_Anexo_I_Leiaute.pdf   (versao antes da secao)

    Returns:
        dict com 'documento', 'versao', 'secao', 'titulo'
    """
    metadata = {
        "documento": "",
        "versao": "",
        "secao": "",
        "titulo": "",
    }

    if filename:
        name = Path(filename).stem
        m = re.match(r"MOC[_\s](NFe|CTe|MDFe)[_\s]*(.*)$", name, re.IGNORECASE)
        if m:
            doc_prefix = m.group(1).upper()
            if doc_prefix == "NFE":
                metadata["documento"] = "NF-e"
            elif doc_prefix == "CTE":
                metadata["documento"] = "CT-e"
            elif doc_prefix == "MDFE":
                metadata["documento"] = "MDF-e"

            rest = m.group(2).strip()
            # Forma A: "v7.00_Anexo_I_Leiaute" (versao primeiro)
            m2 = re.match(r"v(\d[\d.a-z]*)[_\s]+(.+)$", rest, re.IGNORECASE)
            if m2:
                metadata["versao"] = m2.group(1)
                metadata["secao"] = m2.group(2).replace("_", " ").strip()
            else:
                # Forma B: "VisaoGeral_v4.00" (secao primeiro)
                m3 = re.match(r"(.+?)[_\s]+v(\d[\d.a-z]*)\.?$", rest, re.IGNORECASE)
                if m3:
                    metadata["secao"] = m3.group(1).replace("_", " ").strip()
                    metadata["versao"] = m3.group(2)
                else:
                    metadata["secao"] = rest.replace("_", " ").strip()

    return metadata


def parse_cronograma(page_texts, spans_por_pagina=None):
    """
    Extrai o cronograma da tabela 'Historico de Alteracoes / Cronograma' da NT.

    Le a tabela por coluna (utils/colunas.py) e mantem as celulas literais
    ("Ate 05/10/2026", "Ja implantado", "07/2025"). Nunca inventa versao nem data:
    sem tabela reconhecida devolve [] e avisa ERRO_DATA_NAO_ENCONTRADA.

    Args:
        page_texts: textos das paginas (nao usado para extrair; mantido por compatibilidade)
        spans_por_pagina: lista (uma por pagina) de spans com bbox (cores.extract_page_content)

    Returns:
        lista de dicts com 'versao', 'homologacao', 'producao', 'descricao'
    """
    from utils.colunas import extrair_cronograma_tabela

    cronograma = extrair_cronograma_tabela(spans_por_pagina) if spans_por_pagina else []
    if not cronograma:
        LOG.warning("ERRO_DATA_NAO_ENCONTRADA: tabela de cronograma nao reconhecida; cronograma = []")
    return cronograma


def parse_sections(page_texts):
    """
    Identifica secoes numeradas e seus titulos.

    Returns:
        lista de dicts com 'numero', 'titulo', 'texto'
    """
    full_text = "\n".join(page_texts)
    sections = []
    current_section = None
    current_text = []

    for line in full_text.split("\n"):
        stripped = line.strip()
        m = PATTERN_SECAO.match(stripped)

        if m:
            # Salvar secao anterior
            if current_section:
                current_section["texto"] = "\n".join(current_text).strip()
                sections.append(current_section)

            current_section = {
                "numero": m.group(1),
                "titulo": m.group(2).strip(),
                "texto": "",
            }
            current_text = []
        elif current_section:
            current_text.append(stripped)

    # Salvar ultima secao
    if current_section:
        current_section["texto"] = "\n".join(current_text).strip()
        sections.append(current_section)

    return sections


def parse_items_from_section(section_text, marcacoes=None):
    """
    Extrai itens individuais de uma secao.

    Args:
        section_text: texto da secao
        marcacoes: lista de marcacoes por span (opcional, do cores.py)

    Returns:
        lista de dicts com 'id', 'tipo', 'texto', 'marcacao'
    """
    items = []
    lines = section_text.split("\n")

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        # Tentar extrair ID de regra/campo
        item_id = ""
        m = PATTERN_REGRA_ID.search(stripped)
        if m:
            item_id = m.group(1)

        # Determinar tipo do item
        tipo = "desconhecido"
        lower = stripped.lower()
        if any(kw in lower for kw in ["rejeição", "rejeicao", "rej.", "cstat", "cstat"]):
            tipo = "regra"
        elif any(kw in lower for kw in ["campo", "tag", "elemento", "leiaute"]):
            tipo = "campo"
        elif any(kw in lower for kw in ["evento", "e1", "e2", "e3", "e4"]):
            tipo = "evento"
        elif item_id:
            # Inferir pelo formato do ID
            if re.match(r"^[A-Z]\d", item_id):
                tipo = "regra"
            elif re.match(r"^e\d", item_id, re.IGNORECASE):
                tipo = "evento"
            elif re.match(r"^\d{4}$", item_id):
                tipo = "regra"
            else:
                tipo = "item"

        # Determinar marcacao
        marcacao = "SEM_MARCA"
        if marcacoes:
            # Encontrar marcacao mais proxima pelo texto
            for m_item in marcacoes:
                if m_item["text"] in stripped or stripped in m_item["text"]:
                    marcacao = m_item["marcacao"]
                    break

        items.append({
            "id": item_id,
            "tipo": tipo,
            "texto": stripped,
            "marcacao": marcacao,
        })

    return items


def parse_moc_sections(page_texts):
    """
    Extrai secoes de um MOC (estrutura hierarquica).

    Returns:
        lista de dicts com 'numero', 'titulo', 'pagina_inicio'
    """
    full_text = "\n".join(page_texts)
    sections = []

    for i, line in enumerate(full_text.split("\n")):
        stripped = line.strip()
        m = PATTERN_SECAO.match(stripped)
        if m:
            sections.append({
                "numero": m.group(1),
                "titulo": m.group(2).strip(),
                "pagina_inicio": 0,  # TODO: mapear pagina
            })

    return sections


def parse_moc_regras(page_texts):
    """
    Extrai regras de validacao de um MOC.

    Returns:
        lista de dicts com 'id', 'cStat', 'descricao', 'secao'
    """
    full_text = "\n".join(page_texts)
    regras = []

    # Procurar tabelas de regras (linhas com ID + cStat + descricao)
    for line in full_text.split("\n"):
        stripped = line.strip()
        if not stripped:
            continue

        # Pattern: "C17-10" ou "5E17-70" seguido de codigo e descricao
        m = re.match(r"([A-Z]?\d[\w-]+)\s+(.+)", stripped)
        if m:
            regras.append({
                "id": m.group(1),
                "cStat": "",
                "descricao": m.group(2).strip()[:200],
                "secao": "",
            })

    return regras


def parse_moc_campos(page_texts):
    """
    Extrai campos do leiaute de um MOC.

    Returns:
        lista de dicts com 'tag', 'tipo', 'minOccurs', 'maxOccurs', 'descricao'
    """
    full_text = "\n".join(page_texts)
    campos = []

    # Procurar padroes de campos XML (tag, tipo, ocorrencia)
    for line in full_text.split("\n"):
        stripped = line.strip()
        if not stripped:
            continue

        # Pattern: tag XML seguida de descricao
        m = re.match(r"<(\w+)>\s*(.*)", stripped)
        if m:
            campos.append({
                "tag": m.group(1),
                "tipo": "",
                "minOccurs": "",
                "maxOccurs": "",
                "descricao": m.group(2).strip()[:200],
            })

    return campos