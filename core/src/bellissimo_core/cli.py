"""Línea de comandos del proyecto.

Uso:
    uv run bellissimo validar             # revisa data/menu.yaml
    uv run bellissimo validar --archivo X # revisa otro archivo
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from bellissimo_core import __version__
from bellissimo_core.loader import CartaInvalidaError, cargar_carta, encontrar_carta


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="bellissimo",
        description="Herramientas de la carta de Bellissimo.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="comando", metavar="comando")

    validar = sub.add_parser("validar", help="revisa que la carta cumpla todas las reglas")
    validar.add_argument(
        "--archivo",
        type=Path,
        help="ruta del YAML (por defecto, busca data/menu.yaml)",
    )
    return parser


def comando_validar(archivo: Path | None) -> int:
    try:
        ruta = archivo or encontrar_carta()
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    try:
        carta = cargar_carta(ruta)
    except CartaInvalidaError as exc:
        print(f"La carta tiene {len(exc.errores)} error(es) en {ruta}:", file=sys.stderr)
        for error in exc.errores:
            print(f"  • {error}", file=sys.stderr)
        return 1

    platos = sum(1 for _ in carta.todos_los_platos())
    print(f"Carta válida: {len(carta.secciones)} secciones y {platos} productos.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.comando == "validar":
        return comando_validar(args.archivo)
    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
