"""Reglas de validación de la carta.

Cada prueba parte de una carta válida, rompe una sola regla y verifica que
la validación la detecte con un mensaje que apunte al lugar correcto.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from bellissimo_core.loader import CartaInvalidaError, cargar_carta, validar_datos
from bellissimo_core.models import Carta


def errores_de(datos: dict[str, Any]) -> list[str]:
    """Valida y devuelve la lista de errores (falla si la carta resultara válida)."""
    with pytest.raises(CartaInvalidaError) as exc:
        validar_datos(datos)
    return exc.value.errores


def test_la_carta_minima_es_valida(carta_minima: dict[str, Any]) -> None:
    carta = validar_datos(carta_minima)
    assert isinstance(carta, Carta)
    assert carta.plato("tiramisu").precio == 12000


# ── Precios ──────────────────────────────────────────────────────────────────


@pytest.mark.parametrize("precio", [0, -5000])
def test_precio_debe_ser_positivo(carta_minima: dict[str, Any], precio: int) -> None:
    carta_minima["secciones"][0]["platos"][0]["precio"] = precio
    (error,) = errores_de(carta_minima)
    assert error.startswith("secciones → 0 → platos → 0 → precio")


def test_precio_debe_ser_multiplo_de_100(carta_minima: dict[str, Any]) -> None:
    carta_minima["secciones"][0]["platos"][0]["precio"] = 12050
    (error,) = errores_de(carta_minima)
    assert "multiple of 100" in error


@pytest.mark.parametrize(
    "precio",
    [
        12.0,  # lo que YAML entrega cuando alguien escribe `precio: 12.000`
        "12.000",  # lo que entrega si lo escribe entre comillas
        "12000",  # un número escrito como texto tampoco es válido
        True,  # en Python, True cuenta como el entero 1
    ],
)
def test_precio_escrito_como_no_entero_da_un_mensaje_claro(
    carta_minima: dict[str, Any], precio: object
) -> None:
    carta_minima["secciones"][0]["platos"][0]["precio"] = precio
    (error,) = errores_de(carta_minima)
    assert error.startswith("secciones → 0 → platos → 0 → precio")
    assert "número entero sin puntos ni comas, por ejemplo 13000" in error


def test_yaml_lee_el_punto_de_miles_como_decimal(tmp_path: Path, ruta_carta_real: Path) -> None:
    """Prueba de extremo a extremo con el error más común al editar la carta."""
    texto = ruta_carta_real.read_text(encoding="utf-8")
    archivo = tmp_path / "menu.yaml"
    archivo.write_text(texto.replace("precio: 19000", "precio: 19.000", 1), encoding="utf-8")
    with pytest.raises(CartaInvalidaError) as exc:
        cargar_carta(archivo)
    (error,) = exc.value.errores
    assert "se recibió 19.0" in error


# ── Identificadores ─────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "id_invalido", ["Tiramisu", "tiramisú", "tira misu", "tira--misu", "-tiramisu"]
)
def test_id_con_formato_invalido(carta_minima: dict[str, Any], id_invalido: str) -> None:
    carta_minima["secciones"][0]["platos"][0]["id"] = id_invalido
    (error,) = errores_de(carta_minima)
    assert error.startswith("secciones → 0 → platos → 0 → id")


def test_ids_de_plato_repetidos_en_secciones_distintas(carta_minima: dict[str, Any]) -> None:
    # El id repetido está en una proteína y en un postre: la regla es global.
    carta_minima["secciones"][0]["platos"][0]["id"] = "albondigas"
    (error,) = errores_de(carta_minima)
    assert "mismo id: albondigas" in error


def test_ids_de_seccion_repetidos(carta_minima: dict[str, Any]) -> None:
    otra = {
        "id": "postres",
        "titulo": "Más postres",
        "platos": [{"id": "flan", "nombre": "Flan", "precio": 9000}],
    }
    carta_minima["secciones"].append(otra)
    (error,) = errores_de(carta_minima)
    assert "secciones con el mismo id: postres" in error


# ── Estructura ──────────────────────────────────────────────────────────────


def test_campo_desconocido_se_rechaza(carta_minima: dict[str, Any]) -> None:
    # Un error de tipeo no debe ignorarse en silencio.
    carta_minima["secciones"][0]["platos"][0]["precoi"] = 12000
    errores = errores_de(carta_minima)
    assert any("precoi" in e for e in errores)


def test_seccion_con_platos_y_grupos_a_la_vez(carta_minima: dict[str, Any]) -> None:
    carta_minima["secciones"][0]["grupos"] = [
        {"nombre": "Fríos", "platos": [{"id": "helado", "nombre": "Helado", "precio": 6000}]}
    ]
    (error,) = errores_de(carta_minima)
    assert "`platos` o `grupos`" in error


def test_seccion_vacia(carta_minima: dict[str, Any]) -> None:
    carta_minima["secciones"][0]["platos"] = []
    (error,) = errores_de(carta_minima)
    assert "`platos` o `grupos`" in error


def test_opciones_repetidas(carta_minima: dict[str, Any]) -> None:
    carta_minima["secciones"][0]["platos"][0]["opciones"] = ["Clásico", "Clásico"]
    (error,) = errores_de(carta_minima)
    assert "opciones repetidas: Clásico" in error


def test_una_sola_opcion_no_tiene_sentido(carta_minima: dict[str, Any]) -> None:
    carta_minima["secciones"][0]["platos"][0]["opciones"] = ["Clásico"]
    (error,) = errores_de(carta_minima)
    assert "al menos dos" in error


def test_color_de_salsa_desconocido(carta_minima: dict[str, Any]) -> None:
    carta_minima["arma_tu_pasta"]["salsas"][0]["color"] = "morada"
    (error,) = errores_de(carta_minima)
    assert error.startswith("arma_tu_pasta → salsas → 0 → color")


# ── Restaurante y horario ───────────────────────────────────────────────────


@pytest.mark.parametrize("numero", ["3150336914", "+573150336914", "57 315 033 6914"])
def test_whatsapp_debe_llevar_indicativo_y_solo_numeros(
    carta_minima: dict[str, Any], numero: str
) -> None:
    carta_minima["restaurante"]["whatsapp"] = numero
    (error,) = errores_de(carta_minima)
    assert error.startswith("restaurante → whatsapp")


def test_cierre_antes_de_apertura(carta_minima: dict[str, Any]) -> None:
    carta_minima["horario"]["lunes"] = {"abre": "20:00", "cierra": "12:30"}
    (error,) = errores_de(carta_minima)
    assert error.startswith("horario → lunes")
    assert "posterior" in error


def test_dia_olvidado_es_error_y_no_cerrado(carta_minima: dict[str, Any]) -> None:
    del carta_minima["horario"]["jueves"]
    (error,) = errores_de(carta_minima)
    assert error.startswith("horario → jueves")


def test_horario_del_dia(carta_minima: dict[str, Any]) -> None:
    horario = validar_datos(carta_minima).horario
    assert horario.del_dia(1) is None  # martes: cerrado
    domingo = horario.del_dia(6)
    assert domingo is not None
    assert f"{domingo.cierra:%H:%M}" == "19:00"


# ── Inmutabilidad ───────────────────────────────────────────────────────────


def test_la_carta_no_se_puede_modificar(carta_minima: dict[str, Any]) -> None:
    carta = validar_datos(carta_minima)
    with pytest.raises(ValueError, match="frozen"):
        carta.plato("tiramisu").precio = 1  # type: ignore[misc]


def test_lista_vacia_da_un_solo_error_claro(carta_minima: dict[str, Any]) -> None:
    carta_minima["arma_tu_pasta"]["proteinas"] = []
    (error,) = errores_de(carta_minima)
    assert error == "arma_tu_pasta → proteinas: debe tener al menos un elemento"


def test_un_plato_invalido_no_reporta_ademas_lista_vacia(carta_minima: dict[str, Any]) -> None:
    # El único postre tiene un precio inválido: debe salir UN error (el del
    # precio), no también "la sección quedó sin platos".
    carta_minima["secciones"][0]["platos"][0]["precio"] = -1
    assert len(errores_de(carta_minima)) == 1
