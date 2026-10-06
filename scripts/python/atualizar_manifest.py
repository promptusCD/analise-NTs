#!/usr/bin/env python3
"""
atualizar_manifest.py - Atualiza status de ingestao no manifest.yaml.

Uso:
    python atualizar_manifest.py --arquivo <path> --status <status>
    python atualizar_manifest.py --list
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.manifest import atualizar_status_manifest, listar_manifest


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Gerencia status de ingestao no manifest.yaml"
    )
    parser.add_argument("--arquivo", help="Caminho do arquivo no manifest")
    parser.add_argument(
        "--status",
        choices=["pendente", "extraida", "revisada"],
        help="Novo status de ingestao",
    )
    parser.add_argument("--list", action="store_true", help="Listar status de todas as entradas")
    parser.add_argument("--manifest", default="manifest.yaml", help="Caminho para manifest.yaml")

    args = parser.parse_args()

    if args.list:
        entradas = listar_manifest(args.manifest)
        print(f"\n{'ID':<30} {'Documento':<10} {'Tipo':<15} {'NT':<12} {'Versao':<10} {'Status':<12}")
        print("-" * 90)
        for e in entradas:
            print(
                f"{e['id']:<30} {e['documento']:<10} {e['tipo']:<15} {e['nt']:<12} {e['versao']:<10} {e['status']:<12}"
            )
        print(f"\nTotal: {len(entradas)} entradas")
        return

    if not args.arquivo or not args.status:
        parser.error("Especifique --arquivo e --status, ou use --list")

    atualizado = atualizar_status_manifest(args.arquivo, args.status, args.manifest)

    if atualizado:
        print(f"Atualizado: {args.arquivo} -> {args.status}")
    else:
        print(f"ERRO: Nao encontrou entrada para: {args.arquivo}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()