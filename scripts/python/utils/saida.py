"""
utils/saida.py - Geracao de JSON e MD para NTs e MOCs.

Formato conforme REFERENCIA.md secao 5.1.
"""

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path


def calcular_estatisticas(itens):
    """
    Calcula estatisticas de marcacao dos itens.

    Returns:
        dict com 'total_itens' e 'por_marcacao'
    """
    por_marcacao = {
        "AMARELO": 0,
        "VERDE": 0,
        "EXCLUIDO": 0,
        "SEM_MARCA": 0,
    }

    for item in itens:
        marcacao = item.get("marcacao", "SEM_MARCA")
        if marcacao in por_marcacao:
            por_marcacao[marcacao] += 1
        else:
            # Marcacao desconhecida (VERMELHO_TEXTO, RISCADO_SEM_COR, etc.)
            por_marcacao["SEM_MARCA"] += 1

    return {
        "total_itens": len(itens),
        "por_marcacao": por_marcacao,
    }


def gerar_json_nt(metadata, cronograma, itens, arquivo_origem, sha256):
    """
    Gera JSON conforme formato REFERENCIA.md secao 5.1.

    Args:
        metadata: dict com nt, versao, documento, titulo
        cronograma: lista de dicts com versao, homologacao, producao
        itens: lista de dicts com id, tipo, secao, secao_titulo, pagina, texto, marcacoes
        arquivo_origem: caminho do arquivo original
        sha256: hash SHA256 do arquivo

    Returns:
        dict no formato JSON
    """
    estatisticas = calcular_estatisticas(itens)

    return {
        "nt": metadata.get("nt", ""),
        "versao": metadata.get("versao", ""),
        "documento": metadata.get("documento", ""),
        "titulo": metadata.get("titulo", ""),
        "arquivo_origem": str(arquivo_origem),
        "sha256": sha256,
        "extraido_em": datetime.now(timezone.utc).isoformat(),
        "tipo_documento": "NT",
        "cronograma": cronograma,
        "itens": itens,
        "estatisticas": estatisticas,
    }


def gerar_md_nt(json_data):
    """
    Gera MD legivel com cabecalho, secoes e itens destacados por marcacao.

    Args:
        json_data: dict no formato gerado por gerar_json_nt

    Returns:
        str com conteudo MD
    """
    lines = []
    lines.append(f"# NT {json_data['nt']} v{json_data['versao']} - {json_data['documento']}")
    lines.append("")
    lines.append(f"**Titulo:** {json_data['titulo']}")
    lines.append(f"**Arquivo:** {json_data['arquivo_origem']}")
    lines.append(f"**SHA256:** {json_data['sha256']}")
    lines.append(f"**Extraido em:** {json_data['extraido_em']}")
    lines.append("")

    # Cronograma
    if json_data.get("cronograma"):
        lines.append("## Cronograma")
        lines.append("")
        lines.append("| Versao | Homologacao | Producao |")
        lines.append("|--------|-------------|----------|")
        for c in json_data["cronograma"]:
            lines.append(f"| {c['versao']} | {c['homologacao']} | {c['producao']} |")
        lines.append("")

    # Estatisticas
    stats = json_data.get("estatisticas", {})
    lines.append("## Estatisticas")
    lines.append("")
    lines.append(f"- **Total de itens:** {stats.get('total_itens', 0)}")
    por_m = stats.get("por_marcacao", {})
    lines.append(f"- **AMARELO:** {por_m.get('AMARELO', 0)}")
    lines.append(f"- **VERDE:** {por_m.get('VERDE', 0)}")
    lines.append(f"- **EXCLUIDO:** {por_m.get('EXCLUIDO', 0)}")
    lines.append(f"- **SEM_MARCA:** {por_m.get('SEM_MARCA', 0)}")
    lines.append("")

    # Itens por secao
    secoes = {}
    for item in json_data.get("itens", []):
        sec = item.get("secao", "Geral")
        if sec not in secoes:
            secoes[sec] = []
        secoes[sec].append(item)

    for sec_num, sec_items in sorted(secoes.items()):
        sec_titulo = sec_items[0].get("secao_titulo", "") if sec_items else ""
        if sec_num == "0" and sec_titulo == "Geral":
            lines.append(f"## Conteudo Principal")
        else:
            lines.append(f"## {sec_num}. {sec_titulo}")
        lines.append("")

        # Processar itens - cada item como linha separada com formatacao
        for item in sec_items:
            marcacao = item.get("marcacao", "SEM_MARCA")
            text = item.get("text", "").strip()

            if not text:
                continue

            # Detectar se e um bullet point (comeca com • ou caractere similar)
            is_bullet = text.startswith(("•", "", "-", "*"))

            # Adicionar prefixo de marcacao se necessario
            prefix = ""
            if marcacao != "SEM_MARCA":
                if marcacao == "AMARELO":
                    prefix = "**[AMARELO]** "
                elif marcacao == "VERDE":
                    prefix = "**[VERDE]** "
                elif marcacao == "EXCLUIDO":
                    prefix = "~~**[EXCLUIDO]**~~ "
                elif marcacao == "VERMELHO_TEXTO":
                    prefix = "**[VERMELHO]** "

            # Formatar saida
            if is_bullet:
                # Bullet points - manter como lista
                clean_text = text.lstrip("•-* ").strip()
                lines.append(f"- {prefix}{clean_text}")
            else:
                # Texto normal - adicionar como linha simples
                lines.append(f"{prefix}{text}")

        lines.append("")

    return "\n".join(lines)


def gerar_json_moc(metadata, secoes, regras, campos, arquivo_origem, sha256):
    """
    Gera JSON para MOC.

    Returns:
        dict no formato JSON
    """
    return {
        "documento": metadata.get("documento", ""),
        "versao": metadata.get("versao", ""),
        "secao": metadata.get("secao", ""),
        "titulo": metadata.get("titulo", ""),
        "arquivo_origem": str(arquivo_origem),
        "sha256": sha256,
        "extraido_em": datetime.now(timezone.utc).isoformat(),
        "tipo_documento": "MOC",
        "secoes": secoes,
        "regras": regras,
        "campos": campos,
    }


def gerar_md_moc(json_data):
    """
    Gera MD legivel para MOC.

    Returns:
        str com conteudo MD
    """
    lines = []
    lines.append(f"# MOC {json_data['documento']} v{json_data['versao']}")
    lines.append("")
    lines.append(f"**Secao:** {json_data.get('secao', '')}")
    lines.append(f"**Arquivo:** {json_data['arquivo_origem']}")
    lines.append(f"**SHA256:** {json_data['sha256']}")
    lines.append(f"**Extraido em:** {json_data['extraido_em']}")
    lines.append("")

    # Secoes
    if json_data.get("secoes"):
        lines.append("## Secoes")
        lines.append("")
        for sec in json_data["secoes"]:
            lines.append(f"- **{sec['numero']}** - {sec['titulo']}")
        lines.append("")

    # Regras
    if json_data.get("regras"):
        lines.append(f"## Regras de Validacao ({len(json_data['regras'])} encontradas)")
        lines.append("")
        for regra in json_data["regras"][:50]:  # Limitar a 50 para nao ficar enorme
            cstat = f" (cStat: {regra['cStat']})" if regra.get("cStat") else ""
            lines.append(f"- `{regra['id']}`{cstat}: {regra['descricao']}")
        if len(json_data["regras"]) > 50:
            lines.append(f"- ... e mais {len(json_data['regras']) - 50} regras")
        lines.append("")

    # Campos
    if json_data.get("campos"):
        lines.append(f"## Campos do Leiaute ({len(json_data['campos'])} encontrados)")
        lines.append("")
        for campo in json_data["campos"][:50]:
            lines.append(f"- `{campo['tag']}`: {campo['descricao']}")
        if len(json_data["campos"]) > 50:
            lines.append(f"- ... e mais {len(json_data['campos']) - 50} campos")
        lines.append("")

    return "\n".join(lines)


def salvar_saida(json_data, md_content, output_dir, json_filename, md_filename):
    """
    Salva JSON e MD nos diretorios corretos.

    Args:
        json_data: dict do JSON
        md_content: string do MD
        output_dir: diretorio base (ex: catalogo/nt/nfe/)
        json_filename: nome do arquivo JSON
        md_filename: nome do arquivo MD
    """
    os.makedirs(output_dir, exist_ok=True)

    json_path = os.path.join(output_dir, json_filename)
    md_path = os.path.join(output_dir, md_filename)

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    return json_path, md_path