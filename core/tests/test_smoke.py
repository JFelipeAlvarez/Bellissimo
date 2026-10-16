"""Prueba de humo: confirma que el paquete se instala y la CLI arranca.

Si esta prueba falla, el problema está en el entorno (instalación, versión
de Python), no en la lógica del negocio.
"""

import pytest

from bellissimo_core import __version__
from bellissimo_core.cli import main


def test_paquete_tiene_version() -> None:
    assert __version__ == "0.1.0"


def test_cli_sin_argumentos_termina_bien() -> None:
    assert main([]) == 0


def test_cli_version(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as salida:
        main(["--version"])
    assert salida.value.code == 0
    assert "0.1.0" in capsys.readouterr().out
