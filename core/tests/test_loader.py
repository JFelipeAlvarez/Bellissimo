"""Lectura de archivos y la carta real del restaurante."""

from __future__ import annotations

from pathlib import Path

import pytest

from bellissimo_core.loader import CartaInvalidaError, cargar_carta, encontrar_carta


def test_la_carta_real_es_valida(ruta_carta_real: Path) -> None:
    """La prueba más importante: data/menu.yaml cumple todas las reglas."""
    carta = cargar_carta(ruta_carta_real)
    assert carta.restaurante.nombre == "Bellissimo"


def test_la_carta_real_tiene_los_platos_clave(ruta_carta_real: Path) -> None:
    """Platos que el restaurante confirmó explícitamente."""
    carta = cargar_carta(ruta_carta_real)
    assert carta.plato("salmon").precio == 19000
    assert carta.plato("salsa-pesto").precio == 10000
    assert carta.plato("salsa-camaron").precio == 15000
    assert carta.horario.martes is None


def test_encontrar_carta_desde_una_subcarpeta(ruta_carta_real: Path) -> None:
    raiz = ruta_carta_real.parents[1]
    assert encontrar_carta(raiz / "core" / "tests") == ruta_carta_real


def test_encontrar_carta_sin_archivo(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        encontrar_carta(tmp_path)


def test_archivo_que_no_existe(tmp_path: Path) -> None:
    with pytest.raises(CartaInvalidaError, match="no se pudo leer"):
        cargar_carta(tmp_path / "no-existe.yaml")


def test_yaml_mal_formado(tmp_path: Path) -> None:
    archivo = tmp_path / "menu.yaml"
    archivo.write_text("restaurante:\n  nombre: [sin cerrar\n", encoding="utf-8")
    with pytest.raises(CartaInvalidaError, match="no es YAML válido"):
        cargar_carta(archivo)


def test_yaml_no_ejecuta_codigo(tmp_path: Path) -> None:
    """safe_load rechaza etiquetas que construyen objetos de Python."""
    archivo = tmp_path / "menu.yaml"
    archivo.write_text(
        "restaurante: !!python/object/apply:os.system ['echo hola']\n", encoding="utf-8"
    )
    with pytest.raises(CartaInvalidaError, match="no es YAML válido"):
        cargar_carta(archivo)
