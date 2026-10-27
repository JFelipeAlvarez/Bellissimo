"""Modelos de la carta.

Cada clase describe una parte de `data/menu.yaml` y las reglas que debe
cumplir. Pydantic revisa esas reglas al crear los objetos: si un dato no las
cumple, la carta completa se rechaza con un mensaje que indica dónde está el
error. Así, una carta inválida nunca llega a publicarse.

Convenciones:
- Los precios son enteros en pesos colombianos (ver ADR 0004).
- Los modelos son inmutables (`frozen=True`): una vez cargada, la carta no
  cambia por accidente en ninguna parte del programa.
- Se rechazan campos desconocidos (`extra="forbid"`): si alguien escribe
  `precoi` en lugar de `precio`, el error se detecta de inmediato en vez de
  ignorarse en silencio.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterator
from datetime import time
from enum import StrEnum
from typing import Annotated, Self
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import (
    AfterValidator,
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    StringConstraints,
    model_validator,
)

# ── Tipos reutilizables ─────────────────────────────────────────────────────

Id = Annotated[str, StringConstraints(pattern=r"^[a-z0-9]+(-[a-z0-9]+)*$")]
"""Identificador estable: minúsculas, números y guiones. Ej: `ravioli-carne`."""

Texto = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
"""Texto no vacío; se le quitan los espacios sobrantes de los extremos."""


def _solo_enteros(valor: object) -> object:
    """Rechaza precios que no se escribieron como número entero.

    Ojo: en YAML, `13.000` NO es trece mil: es el número decimal 13,0. Sin
    esta revisión, Pydantic lo convertiría en 13 y el error diría "debe ser
    múltiplo de 100", que no ayuda a encontrar el problema.
    """
    if isinstance(valor, bool) or not isinstance(valor, int):
        raise ValueError(
            f"el precio debe ser un número entero sin puntos ni comas, "
            f"por ejemplo 13000 (se recibió {valor!r})"
        )
    return valor


Pesos = Annotated[int, BeforeValidator(_solo_enteros), Field(gt=0, le=1_000_000, multiple_of=100)]
"""Precio en pesos colombianos: entero positivo, múltiplo de 100."""


def _no_vacia[T](valores: tuple[T, ...]) -> tuple[T, ...]:
    if not valores:
        raise ValueError("debe tener al menos un elemento")
    return valores


type NoVacia[T] = Annotated[tuple[T, ...], AfterValidator(_no_vacia)]
"""Lista con al menos un elemento.

Se valida *después* de revisar cada elemento, así que si un plato tiene un
error, solo se reporta ese error y no, además, que la lista quedó vacía.
"""


def _zona_horaria_valida(nombre: str) -> str:
    try:
        ZoneInfo(nombre)
    except (ZoneInfoNotFoundError, ValueError) as exc:
        raise ValueError(f"'{nombre}' no es una zona horaria válida (ej. America/Bogota)") from exc
    return nombre


class Modelo(BaseModel):
    """Configuración común a todos los modelos de la carta."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        # En el JSON Schema de salida (lo que exporta Python), los campos con
        # valor por defecto también son obligatorios: carta.json siempre los
        # trae, así TypeScript no tiene que preguntar si existen.
        json_schema_serialization_defaults_required=True,
    )


# ── Información del restaurante ─────────────────────────────────────────────


class Restaurante(Modelo):
    nombre: Texto
    lema: Texto
    descripcion: Texto
    direccion: Texto
    whatsapp: Annotated[str, StringConstraints(pattern=r"^57\d{10}$")]
    """Número con indicativo de Colombia y sin espacios: 57 + 10 dígitos."""
    instagram: Annotated[str, StringConstraints(pattern=r"^[a-z0-9._]+$")]
    zona_horaria: Annotated[str, AfterValidator(_zona_horaria_valida)]
    """Zona horaria IANA, por ejemplo `America/Bogota`."""
    alergenos: Texto


class Franja(Modelo):
    """Horario de un día: hora de apertura y de cierre."""

    abre: time
    cierra: time

    @model_validator(mode="after")
    def cierra_despues_de_abrir(self) -> Self:
        if self.cierra <= self.abre:
            raise ValueError(
                f"la hora de cierre ({self.cierra:%H:%M}) debe ser posterior "
                f"a la de apertura ({self.abre:%H:%M})"
            )
        return self


class Horario(Modelo):
    """Horario semanal. `None` en un día significa que ese día está cerrado.

    Los siete días son obligatorios: así un día olvidado en el YAML es un
    error, no un "cerrado" accidental.
    """

    lunes: Franja | None
    martes: Franja | None
    miercoles: Franja | None
    jueves: Franja | None
    viernes: Franja | None
    sabado: Franja | None
    domingo: Franja | None

    def del_dia(self, dia_semana: int) -> Franja | None:
        """Franja de un día, con 0 = lunes … 6 = domingo (como `date.weekday()`)."""
        dias = (
            self.lunes,
            self.martes,
            self.miercoles,
            self.jueves,
            self.viernes,
            self.sabado,
            self.domingo,
        )
        return dias[dia_semana]


# ── Platos ──────────────────────────────────────────────────────────────────


class Plato(Modelo):
    id: Id
    nombre: Texto
    precio: Pesos
    descripcion: Texto | None = None
    opciones: tuple[Texto, ...] = ()
    """Variantes sin costo adicional: sabores, tipos (Original/Zero), etc."""

    @model_validator(mode="after")
    def opciones_sin_repetir(self) -> Self:
        repetidas = [o for o, n in Counter(self.opciones).items() if n > 1]
        if repetidas:
            raise ValueError(f"opciones repetidas: {', '.join(repetidas)}")
        if len(self.opciones) == 1:
            raise ValueError("si un plato tiene opciones, deben ser al menos dos")
        return self


class Salsa(Plato):
    de_la_casa: bool = False


class Grupo(Modelo):
    """Subdivisión con nombre dentro de una sección (ej. "Limonadas")."""

    nombre: Texto
    platos: NoVacia[Plato]


class ColorSalsa(StrEnum):
    ROJA = "roja"
    BLANCA = "blanca"
    VERDE = "verde"


class GrupoSalsas(Modelo):
    nombre: Texto
    color: ColorSalsa
    platos: NoVacia[Salsa]


class GrupoPastas(Modelo):
    nombre: Texto
    platos: NoVacia[Plato]


class ArmaTuPasta(Modelo):
    """El plato armado: pasta obligatoria; salsa y proteína opcionales."""

    incluye: Texto
    pastas: NoVacia[GrupoPastas]
    salsas: NoVacia[GrupoSalsas]
    proteinas: NoVacia[Plato]

    def todas_las_pastas(self) -> Iterator[Plato]:
        for grupo in self.pastas:
            yield from grupo.platos

    def todas_las_salsas(self) -> Iterator[Salsa]:
        for grupo in self.salsas:
            yield from grupo.platos


class Seccion(Modelo):
    """Una sección de la carta. Tiene `platos` o `grupos`, nunca ambos."""

    id: Id
    titulo: Texto
    pestana: Texto | None = None
    """Texto corto para la pestaña de la web; si falta, se usa el título."""
    nota: Texto | None = None
    incluye: Texto | None = None
    platos: tuple[Plato, ...] = ()
    grupos: tuple[Grupo, ...] = ()

    @model_validator(mode="after")
    def platos_o_grupos(self) -> Self:
        if bool(self.platos) == bool(self.grupos):
            raise ValueError("la sección debe tener `platos` o `grupos` (uno de los dos, no ambos)")
        return self

    def todos_los_platos(self) -> Iterator[Plato]:
        yield from self.platos
        for grupo in self.grupos:
            yield from grupo.platos


# ── La carta completa ───────────────────────────────────────────────────────


class Carta(Modelo):
    restaurante: Restaurante
    horario: Horario
    arma_tu_pasta: ArmaTuPasta
    secciones: NoVacia[Seccion]

    def todos_los_platos(self) -> Iterator[Plato]:
        """Recorre cada plato de la carta, incluidos pastas, salsas y proteínas."""
        yield from self.arma_tu_pasta.todas_las_pastas()
        yield from self.arma_tu_pasta.todas_las_salsas()
        yield from self.arma_tu_pasta.proteinas
        for seccion in self.secciones:
            yield from seccion.todos_los_platos()

    def plato(self, id_plato: str) -> Plato:
        """Busca un plato por su id. Lanza `KeyError` si no existe."""
        for p in self.todos_los_platos():
            if p.id == id_plato:
                return p
        raise KeyError(id_plato)

    @model_validator(mode="after")
    def ids_unicos(self) -> Self:
        """Ningún id se repite en toda la carta, ni en platos ni en secciones."""
        repetidos = _repetidos(p.id for p in self.todos_los_platos())
        if repetidos:
            raise ValueError(f"hay platos con el mismo id: {', '.join(repetidos)}")
        repetidas = _repetidos(s.id for s in self.secciones)
        if repetidas:
            raise ValueError(f"hay secciones con el mismo id: {', '.join(repetidas)}")
        return self


def _repetidos(valores: Iterator[str]) -> list[str]:
    return sorted(v for v, n in Counter(valores).items() if n > 1)
