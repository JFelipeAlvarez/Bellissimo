"""Casos de las reglas que no están en los fixtures compartidos.

Son detalles propios de la versión de Python: fechas sin zona horaria,
validación de los datos de entrega, formato de horas, etc.
"""

from __future__ import annotations

from datetime import datetime, time
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from bellissimo_core.horario import estado_atencion, hora_12
from bellissimo_core.loader import CartaInvalidaError, cargar_carta, validar_datos
from bellissimo_core.pedido import (
    LineaArmado,
    LineaPlato,
    Pedido,
    describir_linea,
    precio_unitario,
)
from bellissimo_core.whatsapp import DatosEntrega


@pytest.mark.parametrize(
    ("hora", "texto"),
    [
        (time(0, 0), "12:00 a. m."),
        (time(9, 5), "9:05 a. m."),
        (time(12, 0), "12:00 p. m."),
        (time(12, 30), "12:30 p. m."),
        (time(20, 0), "8:00 p. m."),
        (time(23, 59), "11:59 p. m."),
    ],
)
def test_hora_en_formato_de_12_horas(hora: time, texto: str) -> None:
    assert hora_12(hora) == texto


def test_fecha_sin_zona_horaria_se_rechaza(carta_minima: dict[str, Any]) -> None:
    """Una fecha "ingenua" es ambigua: ¿las 13:00 de dónde?"""
    carta = validar_datos(carta_minima)
    with pytest.raises(ValueError, match="zona horaria"):
        estado_atencion(carta, datetime(2026, 10, 19, 13, 0))


def test_zona_horaria_inexistente_en_la_carta(carta_minima: dict[str, Any]) -> None:
    carta_minima["restaurante"]["zona_horaria"] = "America/Medellin"
    with pytest.raises(CartaInvalidaError, match="no es una zona horaria válida"):
        validar_datos(carta_minima)


def test_horario_sin_ningun_dia_abierto(carta_minima: dict[str, Any]) -> None:
    for dia in carta_minima["horario"]:
        carta_minima["horario"][dia] = None
    carta = validar_datos(carta_minima)
    with pytest.raises(ValueError, match="ningún día abierto"):
        estado_atencion(carta, datetime.fromisoformat("2026-10-19T13:00:00-05:00"))


def test_linea_con_tipo_desconocido_se_rechaza() -> None:
    with pytest.raises(ValidationError):
        Pedido.model_validate({"lineas": [{"tipo": "combo", "id": "x"}]})


def test_describir_linea(carta_minima: dict[str, Any]) -> None:
    carta = validar_datos(carta_minima)
    armado = LineaArmado(tipo="armado", pasta="fettuccine", proteina="albondigas")
    assert describir_linea(carta, armado) == "Fettuccine, sin salsa + Albóndigas"
    plato = LineaPlato(tipo="plato", id="tiramisu")
    assert describir_linea(carta, plato) == "Tiramisú"


@pytest.mark.parametrize("campo", ["nombre", "direccion", "barrio"])
def test_datos_de_entrega_obligatorios(campo: str) -> None:
    datos = {"nombre": "Ana", "direccion": "Calle 10", "barrio": "Centro", "pago": "efectivo"}
    datos[campo] = "   "  # solo espacios cuenta como vacío
    with pytest.raises(ValidationError):
        DatosEntrega.model_validate(datos)


def test_forma_de_pago_desconocida() -> None:
    with pytest.raises(ValidationError):
        DatosEntrega.model_validate(
            {"nombre": "Ana", "direccion": "Calle 10", "barrio": "Centro", "pago": "bitcoin"}
        )


def test_el_ejemplo_de_la_carta_impresa_cuadra_con_los_precios(ruta_carta_real: Path) -> None:
    """La carta impresa muestra este ejemplo con su total. Si un precio cambia
    en data/menu.yaml, esta prueba avisa que el ejemplo impreso quedó viejo."""
    carta = cargar_carta(ruta_carta_real)
    ejemplo = LineaArmado(
        tipo="armado",
        pasta="fettuccine-tinta-calamar",
        salsa="salsa-bolonesa",
        proteina="albondigas-carne",
    )
    assert precio_unitario(carta, ejemplo) == 32500
