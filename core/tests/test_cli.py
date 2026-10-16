"""El comando `bellissimo validar`."""

from __future__ import annotations

from pathlib import Path

import pytest

from bellissimo_core.cli import main


def test_validar_la_carta_real(ruta_carta_real: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["validar", "--archivo", str(ruta_carta_real)]) == 0
    assert "Carta válida" in capsys.readouterr().out


def test_validar_una_carta_con_errores(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    archivo = tmp_path / "menu.yaml"
    archivo.write_text("restaurante: {}\n", encoding="utf-8")
    assert main(["validar", "--archivo", str(archivo)]) == 1
    salida = capsys.readouterr().err
    assert "error(es)" in salida
    assert "restaurante → nombre" in salida
