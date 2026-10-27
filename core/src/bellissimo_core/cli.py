"""Línea de comandos del proyecto.

Uso:
    uv run bellissimo validar              # revisa data/menu.yaml
    uv run bellissimo validar --archivo X  # revisa otro archivo
    uv run bellissimo exportar             # genera los datos para la web
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from bellissimo_core import __version__
from bellissimo_core.export import exportar
from bellissimo_core.loader import CartaInvalidaError, cargar_carta, encontrar_carta
from bellissimo_core.models import Carta

DESTINO_WEB = Path("web") / "src" / "generated"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="bellissimo",
        description="Herramientas de la carta de Bellissimo.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="comando", metavar="comando")

    validar = sub.add_parser("validar", help="revisa que la carta cumpla todas las reglas")
    validar.add_argument(
        "--archivo", type=Path, help="ruta del YAML (por defecto, busca data/menu.yaml)"
    )

    exp = sub.add_parser("exportar", help="genera carta.json y el contrato de tipos para la web")
    exp.add_argument(
        "--archivo", type=Path, help="ruta del YAML (por defecto, busca data/menu.yaml)"
    )
    exp.add_argument(
        "--destino", type=Path, help=f"carpeta de salida (por defecto, {DESTINO_WEB.as_posix()})"
    )
    return parser


def _cargar_o_reportar(archivo: Path | None) -> tuple[Carta, Path] | None:
    """Carga la carta; si falla, imprime los errores y devuelve None."""
    try:
        ruta = archivo or encontrar_carta()
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return None

    try:
        return cargar_carta(ruta), ruta
    except CartaInvalidaError as exc:
        print(f"La carta tiene {len(exc.errores)} error(es) en {ruta}:", file=sys.stderr)
        for error in exc.errores:
            print(f"  • {error}", file=sys.stderr)
        return None


def comando_validar(archivo: Path | None) -> int:
    cargada = _cargar_o_reportar(archivo)
    if cargada is None:
        return 1
    carta, _ = cargada
    platos = sum(1 for _ in carta.todos_los_platos())
    print(f"Carta válida: {len(carta.secciones)} secciones y {platos} productos.")
    return 0


def comando_exportar(archivo: Path | None, destino: Path | None) -> int:
    cargada = _cargar_o_reportar(archivo)
    if cargada is None:
        return 1
    carta, ruta = cargada
    # data/menu.yaml → la raíz del repositorio está dos carpetas arriba.
    salida = destino or ruta.resolve().parents[1] / DESTINO_WEB
    for generado in exportar(carta, salida):
        print(f"Generado: {generado}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.comando == "validar":
        return comando_validar(args.archivo)
    if args.comando == "exportar":
        return comando_exportar(args.archivo, args.destino)
    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
