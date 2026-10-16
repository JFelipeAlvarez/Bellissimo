# Bellissimo

Sistema de carta digital y pedidos a domicilio para **Bellissimo · Pastas para sorprender**, un restaurante de pasta fresca artesanal.

La carta del restaurante vive en un solo archivo de datos ([`data/menu.yaml`](data/menu.yaml)). A partir de él se generan automáticamente:

- **La carta web** para celular, donde el cliente arma su pasta y envía el pedido por WhatsApp.
- **La carta en modo mesa**, la misma página sin opciones de pedido, para el código QR de las mesas.
- **El PDF de imprenta** de la carta física (tríptico).

Cambiar un precio es cambiar una línea; la web y el PDF se actualizan solos.

## Arquitectura en una imagen

```
                 data/menu.yaml  (única fuente de verdad)
                        │
                        ▼
              core/  (Python · Pydantic)
     valida la carta · reglas de precio · horario
                        │
          exporta menu.json + tipos TypeScript
                        │
          ┌─────────────┴─────────────┐
          ▼                           ▼
   web/  (TypeScript · Astro)    tools/pdf/  (Python · Playwright)
   carta web y modo mesa          PDF para la imprenta
          │
          ▼
   GitHub Pages (publicación automática)
```

Las razones de cada decisión están en [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) y en los registros de decisiones de [`docs/adr/`](docs/adr/).

## Estructura del repositorio

| Carpeta | Qué contiene |
|---|---|
| `data/` | La carta: platos, precios, descripciones y horario. |
| `core/` | Paquete de Python: modelos, validación, reglas de negocio y exportador. |
| `web/` | Sitio web en TypeScript con Astro. |
| `shared/fixtures/` | Casos de prueba que comparten Python y TypeScript. |
| `tools/pdf/` | Generador del PDF de imprenta. |
| `docs/` | Arquitectura y decisiones (ADR). |
| `.github/workflows/` | Integración continua y publicación. |

## Requisitos

- [Git](https://git-scm.com/)
- [uv](https://docs.astral.sh/uv/) (instala Python 3.12 automáticamente)
- [Node.js](https://nodejs.org/) 22 LTS

## Primeros pasos

```bash
git clone https://github.com/JFelipeAlvarez/bellissimo.git
cd bellissimo

# Núcleo en Python
cd core
uv sync              # crea el entorno virtual e instala dependencias
uv run pytest        # corre las pruebas
uv run ruff check .  # revisa el estilo del código
cd ..

# Sitio web
cd web
npm ci               # instala dependencias exactas del package-lock.json
npm run dev          # abre la carta en http://localhost:4321
```

## Cómo trabajamos

- **`main` siempre funciona.** Nadie sube cambios directo a `main`; todo entra por *pull request*.
- **Una rama por cambio**, con prefijo según el tipo: `feat/arma-tu-pasta`, `fix/precio-salmon`, `docs/adr-0003`.
- **Commits con [Conventional Commits](https://www.conventionalcommits.org/es/v1.0.0/)**: `feat: agrega salmón a las proteínas`, `fix: corrige horario del domingo`.
- **La integración continua debe pasar** (pruebas, linter y build) antes de fusionar.

## Hoja de ruta

- [x] **Fase 0** · Estructura del proyecto, herramientas y documentación
- [ ] **Fase 1** · Carta como datos, carta web con pedidos por WhatsApp, publicación automática y PDF de imprenta
- [ ] **Fase 2** · Pedidos registrados en base de datos y panel para la cocina (FastAPI + PostgreSQL)
- [ ] **Fase 3** · Pagos en línea, WhatsApp Business API e integración con el POS
- [ ] **Fase 4** · IA: pronóstico de demanda de pasta fresca y asistente de pedidos
