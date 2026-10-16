"""Datos compartidos por las pruebas.

`carta_minima` es la carta válida más pequeña posible. Cada prueba de
validación la copia, rompe UNA cosa y comprueba que se detecte. Así cada
prueba deja claro qué regla está verificando.
"""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

import pytest

RAIZ_REPO = Path(__file__).resolve().parents[2]

_FRANJA = {"abre": "12:30", "cierra": "20:00"}

_CARTA_MINIMA: dict[str, Any] = {
    "restaurante": {
        "nombre": "Bellissimo",
        "lema": "Pastas para sorprender",
        "descripcion": "Pasta fresca artesanal",
        "direccion": "Calle 8 # 4-51",
        "whatsapp": "573150336914",
        "instagram": "bellissimo.pastas",
        "zona_horaria": "America/Bogota",
        "alergenos": "Contiene gluten.",
    },
    "horario": {
        "lunes": _FRANJA,
        "martes": None,
        "miercoles": _FRANJA,
        "jueves": _FRANJA,
        "viernes": _FRANJA,
        "sabado": _FRANJA,
        "domingo": {"abre": "12:30", "cierra": "19:00"},
    },
    "arma_tu_pasta": {
        "incluye": "pan y queso parmesano",
        "pastas": [
            {
                "nombre": "Pastas largas",
                "platos": [{"id": "fettuccine", "nombre": "Fettuccine", "precio": 7000}],
            }
        ],
        "salsas": [
            {
                "nombre": "Rojas",
                "color": "roja",
                "platos": [{"id": "napolitana", "nombre": "Napolitana", "precio": 10000}],
            }
        ],
        "proteinas": [{"id": "albondigas", "nombre": "Albóndigas", "precio": 15000}],
    },
    "secciones": [
        {
            "id": "postres",
            "titulo": "Postres",
            "platos": [{"id": "tiramisu", "nombre": "Tiramisú", "precio": 12000}],
        }
    ],
}


@pytest.fixture
def carta_minima() -> dict[str, Any]:
    """Copia profunda: cada prueba puede modificarla sin afectar a las demás."""
    return copy.deepcopy(_CARTA_MINIMA)


@pytest.fixture
def ruta_carta_real() -> Path:
    return RAIZ_REPO / "data" / "menu.yaml"
