"""
utils/cores.py - Deteccao de marcações de cor em PDFs fiscais.

Detecta:
- Fundo colorido (amarelo, verde) via page.get_drawings()
- Cor do texto (vermelho = indicativo de exclusao)
- Strikethrough via flag FZ_STEXT_STRIKEOUT + deteccao vetorial
- Mapeamento span -> cor de fundo via intersecao de bbox
- Fallback pixmap para PDFs sem retangulos vetoriais
"""

import pymupdf
import math


# Cores de fundo usadas nas NTs (em float RGB 0.0-1.0)
CORES_FUNDO = {
    "AMARELO": (1.0, 1.0, 0.0),
    "VERDE": (0.0, 1.0, 0.0),
}

# Tolerancia para matching de cor (float 0-1)
COR_TOLERANCIA = 0.20

# Cores de texto que indicam exclusao (em hex)
CORES_TEXTO_EXCLUSAO = [
    "#FF0000", "#CC0000", "#C00000", "#B22222",
    "#8B0000", "#FF3333", "#990000",
]


def rgb_close(a, b, tol=COR_TOLERANCIA):
    """Verifica se duas tuplas RGB float estao proximas."""
    if a is None or b is None:
        return False
    if len(a) != len(b):
        return False
    return all(abs(x - y) <= tol for x, y in zip(a, b))


def is_red_text(color_hex):
    """Verifica se a cor do texto e vermelho (indicativo de exclusao)."""
    c = color_hex.upper()
    if c in CORES_TEXTO_EXCLUSAO:
        return True
    try:
        r = int(c[1:3], 16)
        g = int(c[3:5], 16)
        b = int(c[5:7], 16)
        return r > 180 and g < 80 and b < 80
    except (ValueError, IndexError):
        return False


def extract_background_rects(page, target_colors=None):
    """
    Extrai retangulos de fundo colorido de uma pagina.

    Args:
        page: objeto Page do PyMuPDF
        target_colors: dict de {nome: (r,g,b)} para filtrar.
                       Se None, usa CORES_FUNDO.

    Returns:
        lista de dicts com 'rect', 'fill', 'color_name'
    """
    if target_colors is None:
        target_colors = CORES_FUNDO

    rects = []
    paths = page.get_drawings()

    for path in paths:
        if path["fill"] is None:
            continue

        items = path["items"]
        is_rect = any(item[0] == "re" for item in items)
        if not is_rect:
            continue

        rect = path["rect"]
        if rect.width < 3 or rect.height < 3:
            continue
        if rect.width < 5 and rect.height > 50:
            continue  # linha vertical de tabela

        fill = path["fill"]
        rgb = (fill[0], fill[0], fill[0]) if len(fill) == 1 else fill

        color_name = None
        for name, target in target_colors.items():
            if rgb_close(target, rgb):
                color_name = name
                break

        if color_name:
            rects.append({
                "rect": rect,
                "fill": rgb,
                "color_name": color_name,
            })

    return rects


def extract_spans_with_color(page):
    """
    Extrai todos os spans de texto com suas cores, bbox, font, flags.

    Returns:
        lista de dicts com 'text', 'color_hex', 'color_rgb', 'bbox',
        'font', 'size', 'bold', 'italic', 'char_flags'
    """
    flags = pymupdf.TEXTFLAGS_TEXT | pymupdf.TEXT_COLLECT_STYLES
    blocks = page.get_text("dict", flags=flags)["blocks"]
    spans = []

    for block in blocks:
        if block["type"] != 0:
            continue
        for line in block["lines"]:
            for span in line["spans"]:
                text = span["text"].strip()
                if not text:
                    continue

                color_int = span["color"]
                color_rgb = pymupdf.sRGB_to_rgb(color_int)
                color_hex = "#{:02X}{:02X}{:02X}".format(*color_rgb)
                bbox = pymupdf.Rect(span["bbox"])

                spans.append({
                    "text": text,
                    "color_int": color_int,
                    "color_hex": color_hex,
                    "color_rgb": color_rgb,
                    "bbox": bbox,
                    "font": span["font"],
                    "size": round(span["size"], 2),
                    "bold": bool(span["flags"] & (1 << 4)),
                    "italic": bool(span["flags"] & (1 << 1)),
                    "char_flags": span.get("char_flags", 0),
                })

    return spans


def detect_strikethrough(page, spans):
    """
    Detecta strikethrough por flag FZ_STEXT_STRIKEOUT + deteccao vetorial.

    Args:
        page: objeto Page do PyMuPDF
        spans: lista de spans (de extract_spans_with_color)

    Returns:
        lista de dicts com 'span_index', 'method', 'text', 'bbox'
    """
    results = []

    # Metodo 1: Flag FZ_STEXT_STRIKEOUT
    try:
        strikeout_flag = pymupdf.mupdf.FZ_STEXT_STRIKEOUT
    except AttributeError:
        strikeout_flag = 0x08  # fallback

    for i, span in enumerate(spans):
        if span["char_flags"] & strikeout_flag:
            results.append({
                "span_index": i,
                "method": "flag",
                "text": span["text"],
                "bbox": span["bbox"],
            })

    # Metodo 2: Deteccao vetorial - linhas horizontais cruzando texto
    paths = page.get_drawings()
    horizontal_lines = []

    for path in paths:
        for item in path["items"]:
            if item[0] == "l":  # linha
                p1, p2 = item[1], item[2]
                if abs(p1.y - p2.y) < 1.0:
                    line_y = (p1.y + p2.y) / 2
                    line_rect = pymupdf.Rect(
                        min(p1.x, p2.x), line_y - 1,
                        max(p1.x, p2.x), line_y + 1
                    )
                    horizontal_lines.append({
                        "rect": line_rect,
                        "y": line_y,
                        "color": path.get("fill") or path.get("color"),
                        "width": path.get("width", 0),
                    })
            elif item[0] == "re":
                rect = item[1]
                if rect.height < 4 and rect.width > 10:
                    horizontal_lines.append({
                        "rect": rect,
                        "y": (rect.y0 + rect.y1) / 2,
                        "color": path.get("fill") or path.get("color"),
                        "width": rect.height,
                    })

    # Cruzar linhas com spans
    for i, span in enumerate(spans):
        # Skip se ja detectado por flag
        if any(r["span_index"] == i for r in results):
            continue

        bbox = span["bbox"]
        mid_low = bbox.y0 + bbox.height * 0.25
        mid_high = bbox.y0 + bbox.height * 0.75

        for line in horizontal_lines:
            line_y = line["y"]
            if mid_low <= line_y <= mid_high:
                if line["rect"].x0 <= bbox.x1 and line["rect"].x1 >= bbox.x0:
                    overlap_x = min(line["rect"].x1, bbox.x1) - max(line["rect"].x0, bbox.x0)
                    if overlap_x > bbox.width * 0.4:
                        results.append({
                            "span_index": i,
                            "method": "vector",
                            "text": span["text"],
                            "bbox": bbox,
                            "line_y": line_y,
                            "coverage": overlap_x / bbox.width,
                        })
                        break

    return results


def map_spans_to_background(spans, bg_rects):
    """
    Mapeia cada span ao retangulo de fundo que o contem.

    Args:
        spans: lista de spans (de extract_spans_with_color)
        bg_rects: lista de retangulos (de extract_background_rects)

    Returns:
        lista de dicts com 'span_index', 'marcacao', 'bg_color', 'bg_rgb'
    """
    results = []

    for i, span in enumerate(spans):
        bbox = span["bbox"]
        center_x = (bbox.x0 + bbox.x1) / 2
        center_y = (bbox.y0 + bbox.y1) / 2

        bg_color = "SEM_MARCA"
        bg_rgb = None

        for bg in bg_rects:
            r = bg["rect"]
            tol = 2.0
            if (r.x0 - tol <= center_x <= r.x1 + tol and
                    r.y0 - tol <= center_y <= r.y1 + tol):
                bg_color = bg["color_name"]
                bg_rgb = bg["fill"]
                break

        results.append({
            "span_index": i,
            "marcacao": bg_color,
            "bg_color": bg_color,
            "bg_rgb": bg_rgb,
        })

    return results


def get_background_color_pixmap(page, rect, zoom=2):
    """
    Fallback: renderiza a area do bbox como imagem e amostra o pixel.

    Args:
        page: objeto Page do PyMuPDF
        rect: area a renderizar (pymupdf.Rect ou tupla)
        zoom: fator de zoom

    Returns:
        tupla RGB float (0.0-1.0) ou None
    """
    try:
        mat = pymupdf.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat, clip=rect)

        if pix.width > 0 and pix.height > 0:
            x, y = min(1, pix.width - 1), min(1, pix.height - 1)
            pixel = pix.pixel(x, y)
            return (pixel[0] / 255, pixel[1] / 255, pixel[2] / 255)
    except Exception:
        pass
    return None


def extract_page_content(page):
    """
    Extrai todo o conteudo visual de uma pagina com marcacoes de cor.

    Returns:
        lista de dicts com 'text', 'marcacao', 'bg_color', 'text_color',
        'strikethrough', 'bold', 'font', 'size', 'bbox'
    """
    bg_rects = extract_background_rects(page)
    spans = extract_spans_with_color(page)
    strikeout_spans = detect_strikethrough(page, spans)
    bg_mapping = map_spans_to_background(spans, bg_rects)

    strikeout_indices = {r["span_index"] for r in strikeout_spans}

    # Fallback: se nao encontrou retangulos, tentar pixmap
    use_pixmap_fallback = len(bg_rects) == 0

    items = []
    for i, span in enumerate(spans):
        bbox = span["bbox"]
        bg = bg_mapping[i]
        is_strikeout = i in strikeout_indices

        # Fallback pixmap
        if use_pixmap_fallback and bg["marcacao"] == "SEM_MARCA":
            pixmap_rgb = get_background_color_pixmap(page, bbox)
            if pixmap_rgb:
                for name, target in CORES_FUNDO.items():
                    if rgb_close(target, pixmap_rgb, tol=0.25):
                        bg["marcacao"] = name
                        bg["bg_color"] = name
                        bg["bg_rgb"] = pixmap_rgb
                        break

        # Classificar marcacao final
        marcacao = bg["marcacao"]
        if is_red_text(span["color_hex"]):
            marcacao = "EXCLUIDO" if is_strikeout else "VERMELHO_TEXTO"
        elif is_strikeout and marcacao == "SEM_MARCA":
            marcacao = "RISCADO_SEM_COR"

        items.append({
            "text": span["text"],
            "marcacao": marcacao,
            "bg_color": bg["bg_color"],
            "text_color": span["color_hex"],
            "strikethrough": is_strikeout,
            "bold": span["bold"],
            "font": span["font"],
            "size": span["size"],
            "bbox": [round(x, 2) for x in [bbox.x0, bbox.y0, bbox.x1, bbox.y1]],
        })

    return items


def aggregate_spans_into_lines(items):
    """
    Agrega spans individuais em linhas coesas.
    Spans na mesma posicao Y (com tolerancia) sao concatenados.

    Returns:
        lista de dicts com 'text', 'marcacao', 'bold', 'size', 'line_y'
    """
    if not items:
        return []

    # Ordenar por Y, depois X
    sorted_items = sorted(items, key=lambda x: (x["bbox"][1], x["bbox"][0]))

    lines = []
    current_line = []
    current_y = None
    y_tolerance = 3.0

    for item in sorted_items:
        y = item["bbox"][1]
        if current_y is None or abs(y - current_y) > y_tolerance:
            if current_line:
                lines.append(_merge_line(current_line))
            current_line = [item]
            current_y = y
        else:
            current_line.append(item)

    if current_line:
        lines.append(_merge_line(current_line))

    return lines


def _merge_line(line_items):
    """Merge spans on the same line into a single item."""
    # Ordenar por X
    sorted_items = sorted(line_items, key=lambda x: x["bbox"][0])

    text_parts = []
    for item in sorted_items:
        t = item["text"].strip()
        if t:
            text_parts.append(t)

    text = " ".join(text_parts)

    # Marcacao: se qualquer span tem marcacao, a linha inteira tem
    marcacao = "SEM_MARCA"
    for item in sorted_items:
        if item["marcacao"] != "SEM_MARCA":
            marcacao = item["marcacao"]
            break

    # Bold: se qualquer span e bold
    bold = any(item["bold"] for item in sorted_items)

    # Size: usar o maior
    size = max(item["size"] for item in sorted_items)

    # Bbox: uniao de todos
    x0 = min(item["bbox"][0] for item in sorted_items)
    y0 = min(item["bbox"][1] for item in sorted_items)
    x1 = max(item["bbox"][2] for item in sorted_items)
    y1 = max(item["bbox"][3] for item in sorted_items)

    return {
        "text": text,
        "marcacao": marcacao,
        "bold": bold,
        "size": size,
        "bbox": [x0, y0, x1, y1],
        "line_y": (y0 + y1) / 2,
    }