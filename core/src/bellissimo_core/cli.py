"""Línea de comandos del proyecto.

Por ahora solo muestra la versión. En la fase 1 se agregan los comandos
`validar` (revisa data/menu.yaml) y `exportar` (genera los datos para la web).
"""

import argparse

from bellissimo_core import __version__


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="bellissimo",
        description="Herramientas de la carta de Bellissimo.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    parser.parse_args(argv)
    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
