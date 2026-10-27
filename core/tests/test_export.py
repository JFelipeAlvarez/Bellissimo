"""El puente hacia la web: `exportar` y el comando `bellissimo exportar`."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from bellissimo_core.cli import main
from bellissimo_core.export import esquema_contrato, exportar
from bellissimo_core.loader import cargar_carta, validar_datos


def _leer(ruta: Path) -> Any:
    return json.loads(ruta.read_text(encoding="utf-8"))


def test_exportar_escribe_los_dos_archivos(carta_minima: dict[str, Any], tmp_path: Path) -> None:
    carta = validar_datos(carta_minima)
    rutas = exportar(carta, tmp_path / "generated")
    assert sorted(r.name for r in rutas) == ["carta.json", "contrato.schema.json"]
    assert all(r.exists() for r in rutas)


def test_carta_json_vuelve_a_ser_la_misma_carta(
    carta_minima: dict[str, Any], tmp_path: Path
) -> None:
    """Ida y vuelta: lo que lee la web es exactamente la carta validada."""
    carta = validar_datos(carta_minima)
    (ruta, _) = exportar(carta, tmp_path)
    assert validar_datos(_leer(ruta)) == carta


def test_carta_json_conserva_tildes(carta_minima: dict[str, Any], tmp_path: Path) -> None:
    carta = validar_datos(carta_minima)
    (ruta, _) = exportar(carta, tmp_path)
    # ensure_ascii=False: "Boloñesa" y no "Bolo\u00f1esa"; más legible en el diff.
    assert "\\u00" not in ruta.read_text(encoding="utf-8")


def test_el_esquema_describe_carta_pedido_y_entrega() -> None:
    esquema = esquema_contrato()
    assert esquema["required"] == ["carta", "pedido", "entrega"]
    definiciones = esquema["$defs"]
    for modelo in ("Carta", "Seccion", "Plato", "LineaPlato", "LineaArmado", "DatosEntrega"):
        assert modelo in definiciones


def test_en_la_carta_todos_los_campos_vienen_siempre() -> None:
    """Modo serialization: la web nunca tiene que adivinar si un campo falta."""
    plato = esquema_contrato()["$defs"]["Plato"]
    assert set(plato["required"]) == {"id", "nombre", "precio", "descripcion", "opciones"}


def test_en_el_pedido_los_valores_por_defecto_son_opcionales() -> None:
    """Modo validation: el navegador puede omitir `cantidad`, `salsa`, `proteina`."""
    armado = esquema_contrato()["$defs"]["LineaArmado"]
    assert set(armado["required"]) == {"tipo", "pasta"}


def test_los_campos_no_llevan_titulo() -> None:
    texto = json.dumps(esquema_contrato())
    assert '"title": "Nombre"' not in texto
    assert '"title": "Carta"' in texto  # los modelos sí conservan su nombre


def test_comando_exportar(
    ruta_carta_real: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    args = ["exportar", "--archivo", str(ruta_carta_real), "--destino", str(tmp_path)]
    assert main(args) == 0
    assert capsys.readouterr().out.count("Generado:") == 2
    assert validar_datos(_leer(tmp_path / "carta.json")) == cargar_carta(ruta_carta_real)


def test_comando_exportar_con_carta_invalida_no_escribe_nada(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    archivo = tmp_path / "menu.yaml"
    archivo.write_text("restaurante: {}\n", encoding="utf-8")
    destino = tmp_path / "salida"
    assert main(["exportar", "--archivo", str(archivo), "--destino", str(destino)]) == 1
    assert "error(es)" in capsys.readouterr().err
    assert not destino.exists()
