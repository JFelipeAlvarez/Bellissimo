# data/

Aquí vive **la carta**: [`menu.yaml`](menu.yaml), la única fuente de verdad del proyecto (ver [ADR 0001](../docs/adr/0001-fuente-unica-de-verdad.md)).

## Cómo cambiar algo de la carta

1. Crea una rama: `git checkout -b feat/nuevo-plato`.
2. Edita `menu.yaml`. Las reglas están al inicio del archivo.
3. Valida desde la carpeta `core/`:
   ```bash
   uv run bellissimo validar
   ```
   Si algo está mal, el comando dice exactamente dónde. Por ejemplo:
   ```
   La carta tiene 1 error(es) en data/menu.yaml:
     • secciones → 4 → platos → 0 → precio: el precio debe ser un número entero sin puntos ni comas, por ejemplo 13000 (se recibió 12.0)
   ```
4. Haz commit, sube la rama y abre un *pull request*. La CI vuelve a validar la carta antes de permitir el merge.

## Estructura

| Bloque | Qué contiene |
|---|---|
| `restaurante` | Nombre, dirección, WhatsApp, Instagram, zona horaria y aviso de alérgenos. |
| `horario` | Apertura y cierre de cada día; `null` significa cerrado. |
| `arma_tu_pasta` | Pastas, salsas (por color) y proteínas que el cliente combina. |
| `secciones` | El resto de la carta. Cada sección tiene `platos` o `grupos` de platos. |

Las reglas que se validan están en [`core/src/bellissimo_core/models.py`](../core/src/bellissimo_core/models.py) y se explican en el [ADR 0004](../docs/adr/0004-precios-enteros-y-validacion-estricta.md).
