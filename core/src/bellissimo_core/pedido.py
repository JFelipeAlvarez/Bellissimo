"""Pedidos y reglas de precio.

Un pedido es una lista de líneas. Cada línea es de uno de dos tipos:

- `plato`: un producto que se pide suelto, con su opción si la tiene
  (Coca-Cola Original o Zero). Se pueden pedir sueltos:
    · los productos de las secciones (una lasaña, una bebida...);
    · las proteínas (unas albóndigas de carne);
    · las salsas, pero como *adición* ("Adición de salsa Boloñesa").
  Las pastas no: una pasta siempre se pide como plato armado.
- `armado`: un plato de "Arma tu pasta": una pasta obligatoria y, si el
  cliente quiere, una salsa y una proteína. Su precio es la suma de las tres.

Todas las funciones son *puras*: reciben la carta y el pedido y devuelven un
resultado, sin leer archivos, ni la hora, ni nada externo. Por eso son fáciles
de probar y dan siempre el mismo resultado con los mismos datos.

Las mismas reglas existen en TypeScript (`web/`), y ambas versiones cumplen
los casos de `shared/fixtures/precios.json` (ver ADR 0002).
"""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field

from bellissimo_core.models import Carta, Plato

CANTIDAD_MAXIMA = 50


# ── Errores ─────────────────────────────────────────────────────────────────


class PedidoInvalidoError(Exception):
    """El pedido no cumple las reglas del negocio.

    `codigo` es estable y no depende del idioma: las pruebas, TypeScript y
    (en la fase 2) la API se comparan contra él. `mensaje` es para personas.
    """

    def __init__(self, codigo: str, mensaje: str) -> None:
        self.codigo = codigo
        self.mensaje = mensaje
        super().__init__(f"[{codigo}] {mensaje}")


# ── Modelos del pedido ──────────────────────────────────────────────────────


class _Linea(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    cantidad: int = 1


class LineaPlato(_Linea):
    tipo: Literal["plato"]
    id: str
    opcion: str | None = None


class LineaArmado(_Linea):
    tipo: Literal["armado"]
    pasta: str
    salsa: str | None = None
    proteina: str | None = None


Linea = Annotated[LineaPlato | LineaArmado, Field(discriminator="tipo")]
"""Una línea del pedido. El campo `tipo` decide cuál de las dos clases es."""


class Pedido(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    lineas: tuple[Linea, ...]


# ── Reglas ──────────────────────────────────────────────────────────────────


def precio_unitario(carta: Carta, linea: LineaPlato | LineaArmado) -> int:
    """Precio de UNA unidad de la línea. Lanza `PedidoInvalidoError` si no es válida."""
    _validar_cantidad(linea.cantidad)
    if isinstance(linea, LineaArmado):
        return _precio_armado(carta, linea)
    return _plato_suelto(carta, linea).precio


def subtotal(carta: Carta, pedido: Pedido) -> int:
    """Suma de todas las líneas (precio unitario × cantidad), sin domicilio."""
    if not pedido.lineas:
        raise PedidoInvalidoError("pedido_vacio", "el pedido no tiene productos")
    return sum(precio_unitario(carta, linea) * linea.cantidad for linea in pedido.lineas)


def describir_linea(carta: Carta, linea: LineaPlato | LineaArmado) -> str:
    """Nombre legible de la línea, como se ve en el mensaje de WhatsApp.

    Ejemplos:
        "Fettuccine tinta de calamar con salsa Boloñesa + Albóndigas de carne"
        "Fettuccine al huevo, sin salsa"
        "Coca-Cola (Zero)"
        "Adición de salsa Boloñesa"
    """
    precio_unitario(carta, linea)  # valida antes de describir
    if isinstance(linea, LineaPlato):
        nombre = carta.plato(linea.id).nombre
        if _es_salsa(carta, linea.id):
            return f"Adición de salsa {nombre}"
        return f"{nombre} ({linea.opcion})" if linea.opcion else nombre

    texto = carta.plato(linea.pasta).nombre
    texto += f" con salsa {carta.plato(linea.salsa).nombre}" if linea.salsa else ", sin salsa"
    if linea.proteina:
        texto += f" + {carta.plato(linea.proteina).nombre}"
    return texto


# ── Detalles internos ───────────────────────────────────────────────────────


def _validar_cantidad(cantidad: int) -> None:
    if not 1 <= cantidad <= CANTIDAD_MAXIMA:
        raise PedidoInvalidoError(
            "cantidad_invalida", f"la cantidad debe estar entre 1 y {CANTIDAD_MAXIMA}"
        )


def _precio_armado(carta: Carta, linea: LineaArmado) -> int:
    atp = carta.arma_tu_pasta
    pastas = {p.id: p for p in atp.todas_las_pastas()}
    salsas = {s.id: s for s in atp.todas_las_salsas()}
    proteinas = {p.id: p for p in atp.proteinas}

    pasta = pastas.get(linea.pasta)
    if pasta is None:
        raise PedidoInvalidoError("no_es_pasta", f"'{linea.pasta}' no es una pasta de la carta")
    total = pasta.precio

    if linea.salsa is not None:
        salsa = salsas.get(linea.salsa)
        if salsa is None:
            raise PedidoInvalidoError("no_es_salsa", f"'{linea.salsa}' no es una salsa de la carta")
        total += salsa.precio

    if linea.proteina is not None:
        proteina = proteinas.get(linea.proteina)
        if proteina is None:
            raise PedidoInvalidoError(
                "no_es_proteina", f"'{linea.proteina}' no es una proteína de la carta"
            )
        total += proteina.precio

    return total


def _pedibles_sueltos(carta: Carta) -> dict[str, Plato]:
    """Productos que se pueden pedir sin armar un plato: todo menos las pastas."""
    atp = carta.arma_tu_pasta
    sueltos: list[Plato] = [p for s in carta.secciones for p in s.todos_los_platos()]
    sueltos += atp.proteinas
    sueltos += atp.todas_las_salsas()  # como adición
    return {p.id: p for p in sueltos}


def _es_salsa(carta: Carta, id_plato: str) -> bool:
    return any(s.id == id_plato for s in carta.arma_tu_pasta.todas_las_salsas())


def _plato_suelto(carta: Carta, linea: LineaPlato) -> Plato:
    """Busca un producto que se pueda pedir suelto y valida su opción."""
    plato = _pedibles_sueltos(carta).get(linea.id)

    if plato is None:
        if any(p.id == linea.id for p in carta.arma_tu_pasta.todas_las_pastas()):
            raise PedidoInvalidoError(
                "solo_en_arma_tu_pasta",
                f"'{linea.id}' es una pasta: se pide con Arma tu pasta, aunque sea sin salsa",
            )
        raise PedidoInvalidoError("plato_inexistente", f"'{linea.id}' no existe en la carta")

    if plato.opciones:
        if linea.opcion is None:
            raise PedidoInvalidoError(
                "falta_opcion", f"elige una opción para {plato.nombre}: {', '.join(plato.opciones)}"
            )
        if linea.opcion not in plato.opciones:
            raise PedidoInvalidoError(
                "opcion_invalida", f"'{linea.opcion}' no es una opción de {plato.nombre}"
            )
    elif linea.opcion is not None:
        raise PedidoInvalidoError("sin_opciones", f"{plato.nombre} no tiene opciones para elegir")

    return plato
