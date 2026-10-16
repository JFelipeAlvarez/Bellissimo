# bellissimo-core

Paquete de Python con el núcleo del sistema: lee y valida la carta (`data/menu.yaml`), aplica las reglas de negocio y exporta los datos para la web.

No sabe nada de HTML ni de PDF. Ver [`docs/ARCHITECTURE.md`](../docs/ARCHITECTURE.md).

## Comandos

```bash
uv sync                    # instala dependencias en .venv
uv run pytest              # pruebas
uv run ruff check .        # linter
uv run ruff format .       # formatea el código
uv run mypy src            # chequeo de tipos
uv run bellissimo --help   # comandos del proyecto
```
