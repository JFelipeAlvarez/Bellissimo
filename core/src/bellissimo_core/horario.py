"""¿Está abierto el restaurante?

La hora es la parte más traicionera de cualquier sistema. Reglas que sigue
este módulo:

1. La hora actual se recibe como parámetro (`ahora`); nunca se lee el reloj
   aquí adentro. Así las pruebas pueden usar cualquier fecha, y la función
   siempre da el mismo resultado con los mismos datos.
2. `ahora` debe traer zona horaria. Un servidor en otro país, o la CI de
   GitHub (que corre en UTC), no puede saber qué hora es en Bogotá con una
   fecha "ingenua" sin zona.
3. Todo se convierte a la zona del restaurante antes de compararlo con el
   horario. Las 01:30 UTC del martes son las 8:30 p. m. del lunes en Bogotá.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

from bellissimo_core.models import Carta

DIAS = ("lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo")


@dataclass(frozen=True)
class EstadoAtencion:
    abierto: bool
    cierra: time | None
    """Hora de cierre de hoy, si está abierto."""
    proxima_apertura: datetime | None
    """Cuándo vuelve a abrir, si está cerrado (en la zona del restaurante)."""
    texto: str
    """Frase lista para mostrar: "Abierto · cierra a las 8:00 p. m."."""


def estado_atencion(carta: Carta, ahora: datetime) -> EstadoAtencion:
    if ahora.tzinfo is None:
        raise ValueError("`ahora` debe tener zona horaria (por ejemplo, datetime.now(UTC))")

    zona = ZoneInfo(carta.restaurante.zona_horaria)
    local = ahora.astimezone(zona)
    hoy = carta.horario.del_dia(local.weekday())

    if hoy is not None and hoy.abre <= local.time() < hoy.cierra:
        return EstadoAtencion(
            abierto=True,
            cierra=hoy.cierra,
            proxima_apertura=None,
            texto=f"Abierto · cierra a las {hora_12(hoy.cierra)}",
        )

    proxima = _proxima_apertura(carta, local)
    return EstadoAtencion(
        abierto=False,
        cierra=None,
        proxima_apertura=proxima,
        texto=f"Cerrado · abrimos {_cuando(local, proxima)} a las {hora_12(proxima.time())}",
    )


def hora_12(hora: time) -> str:
    """Hora en formato de 12 horas, como se dice en Colombia: "8:00 p. m.", "12:30 p. m."."""
    sufijo = "a. m." if hora.hour < 12 else "p. m."
    h = hora.hour % 12 or 12
    return f"{h}:{hora.minute:02d} {sufijo}"


def _proxima_apertura(carta: Carta, local: datetime) -> datetime:
    """Primera apertura posterior a `local`, buscando hasta una semana adelante."""
    for dias in range(8):
        fecha = local.date() + timedelta(days=dias)
        franja = carta.horario.del_dia(fecha.weekday())
        if franja is None:
            continue
        apertura = datetime.combine(fecha, franja.abre, tzinfo=local.tzinfo)
        if apertura > local:
            return apertura
    raise ValueError("el horario no tiene ningún día abierto")


def _cuando(local: datetime, proxima: datetime) -> str:
    diferencia = (proxima.date() - local.date()).days
    if diferencia == 0:
        return "hoy"
    if diferencia == 1:
        return "mañana"
    return f"el {DIAS[proxima.weekday()]}"
