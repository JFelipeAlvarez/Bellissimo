# Guía para asistentes de IA

Contexto del proyecto en `README.md` y `docs/ARCHITECTURE.md`. Reglas al trabajar aquí:

- **La carta solo se edita en `data/menu.yaml`.** Nunca escribas precios ni nombres de platos en `core/`, `web/` o `tools/`. Ver ADR 0001.
- **`core/` no importa nada de presentación** (HTML, PDF, Astro).
- Toda regla de precio nueva lleva un caso en `shared/fixtures/` que se prueba en pytest y en Vitest.
- Antes de proponer un PR, corre en `core/`: `uv run ruff check . && uv run ruff format --check . && uv run mypy src && uv run pytest`; y en `web/`: `npm run build`.
- Commits con Conventional Commits, en español (`feat: ...`, `fix: ...`, `docs: ...`).
- Decisiones de arquitectura nuevas: agrega un ADR en `docs/adr/` en el mismo PR.
- El dueño del proyecto está aprendiendo: en cada PR explica el porqué de las decisiones, no solo el qué.
