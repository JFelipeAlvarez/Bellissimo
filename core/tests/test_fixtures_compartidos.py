"""Casos compartidos con TypeScript (`shared/fixtures/`).

Estos archivos JSON son el contrato entre lenguajes (ADR 0002): describen qué
debe pasar con cada pedido, horario y mensaje. Esta prueba los ejecuta contra
el núcleo de Python; la web los ejecuta contra su versión en TypeScript. Si
alguna de las dos se desvía, su prueba falla.

`pytest.mark.parametrize` convierte cada caso del JSON en una prueba
independiente, con su descripción como nombre.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import pytest

from bellissimo_core.formato import formatear_pesos
from bellissimo_core.horario import estado_atencion
from bellissimo_core.loader import validar_datos
from bellissimo_core.models import Carta
from bellissimo_core.pedido import Pedido, PedidoInvalidoError, precio_unitario, subtotal
from bellissimo_core.whatsapp import DatosEntrega, enlace_whatsapp, mensaje_pedido

FIXTURES = Path(__file__).resolve().parents[2] / "shared" / "fixtures"


def _cargar(nombre: str) -> Any:
    return json.loads((FIXTURES / nombre).read_text(encoding="utf-8"))


PRECIOS = _cargar("precios.json")
HORARIO = _cargar("horario.json")
WHATSAPP = _cargar("whatsapp.json")


def _ids(casos: list[dict[str, Any]]) -> list[str]:
    return [c["descripcion"] for c in casos]


@pytest.fixture(scope="module")
def carta() -> Carta:
    return validar_datos(_cargar("carta.json"))


# ── Precios ──────────────────────────────────────────────────────────────────


@pytest.mark.parametrize(("valor", "esperado"), PRECIOS["formato_pesos"])
def test_formato_pesos(valor: int, esperado: str) -> None:
    assert formatear_pesos(valor) == esperado


@pytest.mark.parametrize("caso", PRECIOS["casos"], ids=_ids(PRECIOS["casos"]))
def test_precio_valido(carta: Carta, caso: dict[str, Any]) -> None:
    pedido = Pedido.model_validate({"lineas": caso["lineas"]})
    assert [precio_unitario(carta, linea) for linea in pedido.lineas] == caso["precios_unitarios"]
    assert subtotal(carta, pedido) == caso["subtotal"]


@pytest.mark.parametrize("caso", PRECIOS["invalidos"], ids=_ids(PRECIOS["invalidos"]))
def test_pedido_invalido(carta: Carta, caso: dict[str, Any]) -> None:
    pedido = Pedido.model_validate({"lineas": caso["lineas"]})
    with pytest.raises(PedidoInvalidoError) as exc:
        subtotal(carta, pedido)
    assert exc.value.codigo == caso["codigo"]


# ── Horario ──────────────────────────────────────────────────────────────────


@pytest.mark.parametrize("caso", HORARIO["casos"], ids=_ids(HORARIO["casos"]))
def test_estado_atencion(carta: Carta, caso: dict[str, Any]) -> None:
    estado = estado_atencion(carta, datetime.fromisoformat(caso["ahora"]))

    assert estado.abierto == caso["abierto"]
    assert (f"{estado.cierra:%H:%M}" if estado.cierra else None) == caso["cierra"]
    proxima = estado.proxima_apertura.isoformat() if estado.proxima_apertura else None
    assert proxima == caso["proxima_apertura"]
    assert estado.texto == caso["texto"]


# ── WhatsApp ─────────────────────────────────────────────────────────────────


@pytest.mark.parametrize("caso", WHATSAPP["casos"], ids=_ids(WHATSAPP["casos"]))
def test_mensaje_whatsapp(carta: Carta, caso: dict[str, Any]) -> None:
    pedido = Pedido.model_validate({"lineas": caso["lineas"]})
    entrega = DatosEntrega.model_validate(caso["entrega"])

    mensaje = mensaje_pedido(carta, pedido, entrega)
    assert mensaje == caso["mensaje"]

    if caso["enlace"] is not None:
        assert enlace_whatsapp(carta.restaurante.whatsapp, mensaje) == caso["enlace"]
