"""Carga y valida `data/menu.yaml`.

Este módulo es el "borde" del sistema: el único lugar donde datos externos
(un archivo que edita una persona) entran al programa. Aquí se validan una
sola vez; de aquí en adelante, el resto del código confía en que la `Carta`
es correcta.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from bellissimo_core.models import Carta

RUTA_RELATIVA = Path("data") / "menu.yaml"


class CartaInvalidaError(Exception):
    """La carta no se pudo leer o no cumple las reglas de los modelos.

    `errores` trae un mensaje por problema, listo para mostrar a una persona.
    """

    def __init__(self, errores: list[str]) -> None:
        self.errores = errores
        super().__init__("\n".join(errores))


def encontrar_carta(desde: Path | None = None) -> Path:
    """Busca `data/menu.yaml` subiendo carpeta por carpeta desde `desde`.

    Permite ejecutar los comandos desde `core/`, desde la raíz del repositorio
    o desde cualquier subcarpeta.
    """
    inicio = (desde or Path.cwd()).resolve()
    for carpeta in (inicio, *inicio.parents):
        candidata = carpeta / RUTA_RELATIVA
        if candidata.is_file():
            return candidata
    raise FileNotFoundError(f"no encontré {RUTA_RELATIVA} desde {inicio}")


def cargar_carta(ruta: Path) -> Carta:
    """Lee y valida la carta. Lanza `CartaInvalidaError` si algo está mal."""
    try:
        texto = ruta.read_text(encoding="utf-8")
    except OSError as exc:
        raise CartaInvalidaError([f"no se pudo leer {ruta}: {exc.strerror}"]) from exc

    try:
        # safe_load solo construye datos simples (dict, list, str, int...).
        # yaml.load sin "safe" podría ejecutar código escondido en el archivo.
        datos: Any = yaml.safe_load(texto)
    except yaml.YAMLError as exc:
        raise CartaInvalidaError([f"el archivo no es YAML válido: {exc}"]) from exc

    return validar_datos(datos)


def validar_datos(datos: Any) -> Carta:
    """Convierte datos ya leídos (dict) en una `Carta` validada."""
    try:
        return Carta.model_validate(datos)
    except ValidationError as exc:
        raise CartaInvalidaError([_describir(e) for e in exc.errors()]) from exc


def _describir(error: Any) -> str:
    """Convierte un error de Pydantic en una línea legible.

    Ej: `secciones → 2 → platos → 0 → precio: Input should be greater than 0`
    """
    ubicacion = " → ".join(str(parte) for parte in error["loc"]) or "carta"
    mensaje = str(error["msg"]).removeprefix("Value error, ")
    return f"{ubicacion}: {mensaje}"
