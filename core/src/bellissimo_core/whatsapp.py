"""Mensaje de pedido para WhatsApp.

En la fase 1 los pedidos a domicilio llegan por WhatsApp (ADR 0003). La web
arma un enlace `https://wa.me/<número>?text=<mensaje>`: al tocarlo, se abre
WhatsApp con el pedido ya escrito y el cliente solo tiene que enviarlo.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Annotated
from urllib.parse import quote

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from bellissimo_core.formato import formatear_pesos
from bellissimo_core.models import Carta
from bellissimo_core.pedido import Pedido, describir_linea, precio_unitario, subtotal

Texto = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=300)]


class FormaDePago(StrEnum):
    EFECTIVO = "efectivo"
    TRANSFERENCIA = "transferencia"


class DatosEntrega(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    nombre: Texto
    direccion: Texto
    barrio: Texto
    pago: FormaDePago
    paga_con: Annotated[int, Field(gt=0)] | None = None
    """Billete con el que paga, para llevar el cambio. Solo aplica en efectivo."""
    notas: Texto | None = None


def mensaje_pedido(carta: Carta, pedido: Pedido, entrega: DatosEntrega) -> str:
    renglones = [f"Hola {carta.restaurante.nombre}, quiero hacer un pedido a domicilio:", ""]

    for linea in pedido.lineas:
        total_linea = precio_unitario(carta, linea) * linea.cantidad
        renglones.append(
            f"• {linea.cantidad} x {describir_linea(carta, linea)} = {formatear_pesos(total_linea)}"
        )

    renglones += [
        "",
        f"Subtotal: {formatear_pesos(subtotal(carta, pedido))} (más domicilio)",
        "",
        f"Nombre: {entrega.nombre}",
        f"Dirección: {entrega.direccion}",
        f"Barrio: {entrega.barrio}",
        f"Pago: {_texto_pago(entrega)}",
    ]
    if entrega.notas:
        renglones.append(f"Notas: {entrega.notas}")

    return "\n".join(renglones)


def enlace_whatsapp(numero: str, mensaje: str) -> str:
    """Enlace que abre WhatsApp con el mensaje ya escrito.

    `safe="!~*'()"` hace que Python codifique exactamente igual que
    `encodeURIComponent` de JavaScript, para que la web y el núcleo generen
    el mismo enlace carácter por carácter.
    """
    return f"https://wa.me/{numero}?text={quote(mensaje, safe="!~*'()")}"


def _texto_pago(entrega: DatosEntrega) -> str:
    if entrega.pago is FormaDePago.TRANSFERENCIA:
        return "Transferencia"
    if entrega.paga_con:
        return f"Efectivo, pago con {formatear_pesos(entrega.paga_con)}"
    return "Efectivo"
