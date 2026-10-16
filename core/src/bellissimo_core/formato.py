"""Formato de valores para mostrar a las personas."""

from __future__ import annotations


def formatear_pesos(valor: int) -> str:
    """Formatea pesos colombianos con punto de miles: 32500 → "$32.500".

    No se usa `locale` porque depende de la configuración del computador
    donde corre el programa; así el resultado es idéntico en Windows, en la
    CI de GitHub y en el navegador.
    """
    return "$" + f"{valor:,}".replace(",", ".")
