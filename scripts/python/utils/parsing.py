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
from pathlib import Path


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


def parse_nt_metadata(page_texts, filename=None):
    """
    Extrai metadados da NT do cabecalho do PDF.

    Args:
        page_texts: lista de textos das paginas (strings)
        filename: nome do arquivo (opcional, para detect_documento)

    Returns:
        dict com 'nt', 'versao', 'documento', 'titulo'
    """
    metadata = {
        "nt": "",
        "versao": "",
        "documento": "",
        "titulo": "",
    }

    # Tentar detectar pelo nome do arquivo
    if filename:
        metadata["documento"] = detect_documento_from_filename(filename)
        name = Path(filename).stem
        for doc, pattern in PATTERNS_FILENAME.items():
            m = pattern.search(name)
            if m:
                metadata["nt"] = f"{m.group(1)}.{m.group(2)}"
                metadata["versao"] = m.group(3)
                # Nao sobrescrever documento se ja detectado pelo prefixo
                if not metadata["documento"]:
                    metadata["documento"] = doc
                break

    # Tentar extrair do conteudo das primeiras paginas
    first_pages = page_texts[:3] if len(page_texts) >= 3 else page_texts
    full_text = "\n".join(first_pages)

    # Pattern: "Nota Tecnica 2026.007" ou "NT 2026.007"
    m = re.search(r"(?:Nota\s+T[eé]cnica|NT)\s+(\d{4}\.\d{3})", full_text, re.IGNORECASE)
    if m and not metadata["nt"]:
        metadata["nt"] = m.group(1)

    # Pattern: "versao 1.10" ou "v1.10"
    m = re.search(r"v(?:ers[aã]o)?\s*([\d.]+)", full_text, re.IGNORECASE)
    if m and not metadata["versao"]:
        metadata["versao"] = m.group(1)

    # Pattern: titulo geralmente na primeira linha nao vazia
    for line in full_text.split("\n"):
        line = line.strip()
        if len(line) > 10 and not line.startswith(("Nota", "NT ", "Ministerio")):
            # Provavelmente e o titulo
            if not metadata["titulo"]:
                metadata["titulo"] = line[:200]
            break

    return metadata


def parse_moc_metadata(page_texts, filename=None):
    """
    Extrai metadados do MOC do cabecalho do PDF.

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
        m = PATTERN_MOC.search(name)
        if m:
            doc_prefix = m.group(1).upper()
            if doc_prefix == "NFE":
                metadata["documento"] = "NF-e"
            elif doc_prefix == "CTE":
                metadata["documento"] = "CT-e"
            elif doc_prefix == "MDFE":
                metadata["documento"] = "MDF-e"
            metadata["secao"] = m.group(2).replace("_", " ")
            metadata["versao"] = m.group(3)

    return metadata


def parse_cronograma(page_texts):
    """
    Extrai datas de homologacao/producao do cronograma da NT.

    Mantem literais como "Ate 05/10/2026" (nao converte para data).

    Returns:
        lista de dicts com 'versao', 'homologacao', 'producao'
    """
    full_text = "\n".join(page_texts)
    cronograma = []

    # Procurar secao de cronograma
    cronograma_section = ""
    lines = full_text.split("\n")
    in_cronograma = False

    for line in lines:
        lower = line.lower().strip()
        if any(kw in lower for kw in ["cronograma", "prazo", "homologa", "produção", "producao"]):
            in_cronograma = True
        if in_cronograma:
            cronograma_section += line + "\n"
            # Parar quando encontrar proxima secao numerada
            if re.match(r"^\d+\.\s+", line.strip()) and "cronograma" not in lower:
                if len(cronograma_section) > 200:  # Ja temos conteudo suficiente
                    break

    # Se nao encontrou secao especifica, usar todo o texto
    if not cronograma_section.strip():
        cronograma_section = full_text

    # Procurar blocos de versao com datas
    # Pattern: "1.00" ou "v1.00" seguido de datas
    version_blocks = re.split(r"(?:vers[aã]o|v)\s*([\d.]+)", cronograma_section)

    current_versao = ""
    for i, block in enumerate(version_blocks):
        if re.match(r"^[\d.]+$", block.strip()):
            current_versao = block.strip()
            continue

        if not current_versao:
            continue

        # Procurar datas no bloco
        dates = PATTERN_DATA.findall(block)
        ate_dates = PATTERN_ATE.findall(block)

        homologacao = ""
        producao = ""

        # Tentar identificar qual e homologacao e qual e producao
        for j, date in enumerate(dates):
            # Geralmente: primeira data = homologacao, segunda = producao
            if j == 0 and not homologacao:
                # Verificar se tem "Ate" antes
                for ate in ate_dates:
                    if ate in date:
                        homologacao = f"Ate {date}"
                        break
                if not homologacao:
                    homologacao = date
            elif j == 1 and not producao:
                producao = date

        if homologacao or producao:
            cronograma.append({
                "versao": current_versao,
                "homologacao": homologacao,
                "producao": producao,
            })

    # Fallback: procurar datas avulsas se nao encontrou blocos
    if not cronograma:
        all_dates = PATTERN_DATA.findall(full_text)
        ate_dates = PATTERN_ATE.findall(full_text)

        if len(all_dates) >= 2:
            homologacao = all_dates[0]
            producao = all_dates[1]
            for ate in ate_dates:
                if ate == homologacao:
                    homologacao = f"Ate {ate}"
            cronograma.append({
                "versao": "1.00",
                "homologacao": homologacao,
                "producao": producao,
            })

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