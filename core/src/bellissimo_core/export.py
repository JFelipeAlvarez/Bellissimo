"""Exporta la carta y el contrato de tipos para la web.

Es el puente entre Python y TypeScript (ADR 0002). Genera dos archivos:

- `carta.json`: la carta ya validada. La web la lee en tiempo de build para
  generar el HTML, y el navegador la usa para calcular precios.
- `contrato.schema.json`: el JSON Schema de los modelos (carta, pedido y
  datos de entrega). Con él, `json-schema-to-typescript` genera los tipos de
  TypeScript. Si un modelo cambia aquí, los tipos de la web cambian solos y
  TypeScript señala todo el código que quedó desactualizado.

Los dos archivos son *generados*: no se editan a mano ni se suben a Git.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic.json_schema import models_json_schema

from bellissimo_core.models import Carta
from bellissimo_core.pedido import Pedido
from bellissimo_core.whatsapp import DatosEntrega


def esquema_contrato() -> dict[str, Any]:
    """JSON Schema de todo lo que comparten Python y TypeScript.

    Cada modelo se describe desde el punto de vista de quien lo produce:

    - La **carta** la produce Python (`carta.json`), así que se usa el modo
      *serialization*: todos sus campos siempre vienen, aunque tengan valor
      por defecto.
    - El **pedido** y los **datos de entrega** los produce el navegador, así
      que se usa el modo *validation*: los campos con valor por defecto
      (`cantidad`, `salsa`, `notas`…) son opcionales.
    """
    referencias, esquema = models_json_schema(
        [(Carta, "serialization"), (Pedido, "validation"), (DatosEntrega, "validation")],
        ref_template="#/$defs/{model}",
    )
    raiz = {
        "title": "Contrato",
        "description": "Tipos compartidos entre core/ (Python) y web/ (TypeScript).",
        "type": "object",
        "properties": {
            "carta": referencias[(Carta, "serialization")],
            "pedido": referencias[(Pedido, "validation")],
            "entrega": referencias[(DatosEntrega, "validation")],
        },
        "required": ["carta", "pedido", "entrega"],
        "additionalProperties": False,
        "$defs": esquema["$defs"],
    }
    limpio: dict[str, Any] = _sin_titulos_de_campos(raiz)
    return limpio


def exportar(carta: Carta, destino: Path) -> list[Path]:
    """Escribe los archivos en `destino` y devuelve sus rutas."""
    destino.mkdir(parents=True, exist_ok=True)
    archivos = {
        "carta.json": carta.model_dump(mode="json"),
        "contrato.schema.json": esquema_contrato(),
    }
    rutas = []
    for nombre, contenido in archivos.items():
        ruta = destino / nombre
        texto = json.dumps(contenido, ensure_ascii=False, indent=2) + "\n"
        ruta.write_text(texto, encoding="utf-8")
        rutas.append(ruta)
    return rutas


def _sin_titulos_de_campos(nodo: Any) -> Any:
    """Quita el `title` de cada campo (no de cada modelo).

    Pydantic le pone título a cada campo ("Nombre", "Precio"…), y el generador
    de TypeScript crea un tipo con nombre para cada título: `Nombre1`,
    `Nombre2`… Sin ellos, los tipos quedan limpios: `nombre: string`.
    """
    if isinstance(nodo, list):
        return [_sin_titulos_de_campos(x) for x in nodo]
    if not isinstance(nodo, dict):
        return nodo
    resultado = {k: _sin_titulos_de_campos(v) for k, v in nodo.items()}
    if isinstance(resultado.get("properties"), dict):
        for campo in resultado["properties"].values():
            if isinstance(campo, dict):
                campo.pop("title", None)
    return resultado
