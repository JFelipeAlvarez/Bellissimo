# Arquitectura

Este documento explica cómo está construido Bellissimo y por qué. Es la referencia para cualquier persona (o asistente de IA) que trabaje en el proyecto.

## Contexto

Bellissimo es un restaurante pequeño de pasta fresca artesanal. Hoy necesita:

1. Una **carta digital** que los clientes abran en el celular, tanto para pedir a domicilio como para consultar en la mesa escaneando un QR.
2. Que los **pedidos a domicilio** lleguen ordenados y con el total calculado, sin errores de transcripción.
3. Una **carta impresa** que nunca quede desactualizada respecto a la digital.

En el local ya existe un POS (HiPOS) donde se registran los pedidos en caja; este sistema no lo reemplaza.

### Restricciones

- **Presupuesto cero en infraestructura** en las primeras fases.
- **Una sola persona** mantiene el código.
- Quien actualiza precios no es necesariamente programador, así que cambiar la carta debe ser simple y difícil de romper.

## Principios

1. **Una sola fuente de verdad.** La carta existe en un único lugar (`data/menu.yaml`). Todo lo demás se genera. Ver [ADR 0001](adr/0001-fuente-unica-de-verdad.md).
2. **El núcleo no sabe de presentación.** `core/` conoce platos, precios y horarios, pero nada de HTML ni de PDF. La web y el PDF son salidas que consumen el núcleo.
3. **Validar en el borde.** Los datos se validan una vez, al entrar al sistema. Si `menu.yaml` tiene un error, el build falla y nada se publica.
4. **Nada de infraestructura antes de necesitarla.** Mientras los pedidos lleguen por WhatsApp, no hay servidor ni base de datos. Ver [ADR 0003](adr/0003-sitio-estatico-sin-backend.md).
5. **Contratos explícitos entre lenguajes.** Python define los modelos; los tipos de TypeScript se generan desde ellos. Ver [ADR 0002](adr/0002-python-nucleo-typescript-web.md).

## Componentes

### `data/menu.yaml`
La carta en un formato legible por personas: secciones, platos, precios, descripciones, opciones (sabores, variantes) y horario de atención.

### `core/` · Python
Paquete `bellissimo_core`.

| Módulo | Responsabilidad |
|---|---|
| `models.py` | Modelos Pydantic de la carta: `Carta`, `Seccion`, `Plato`, `Horario`… |
| `loader.py` | Lee `menu.yaml` y lo convierte en modelos validados. |
| `pedido.py` | Pedidos y reglas de precio: platos sueltos, plato armado (pasta + salsa + proteína), opciones y cantidades. Errores con código estable. |
| `horario.py` | ¿Está abierto? Próxima apertura y texto para mostrar, siempre en la zona horaria del restaurante. |
| `whatsapp.py` | Mensaje del pedido y enlace `wa.me`. |
| `formato.py` | Formato de pesos colombianos (`$32.500`). |
| `export.py` | Genera `carta.json` y el JSON Schema del que salen los tipos de TypeScript. |
| `cli.py` | Comandos: `validar` y `exportar`. |

Todas las funciones de reglas son **puras**: reciben la carta y los datos (incluida la hora actual) como parámetros y no leen nada externo. Por eso se prueban con casos fijos y dan siempre el mismo resultado.

### `web/` · TypeScript + Astro
Genera HTML estático en tiempo de build a partir de `carta.json`. Solo lo interactivo (armar la pasta, el pedido) ejecuta JavaScript en el navegador. Ver [ADR 0005](adr/0005-web-astro-html-estatico-y-tipos-generados.md).

| Carpeta | Responsabilidad |
|---|---|
| `src/generated/` | *Generado, no se edita.* `carta.json`, `contrato.schema.json` y `tipos.ts`. |
| `src/lib/` | Reglas en TypeScript, espejo de `core/`: `pedido.ts`, `horario.ts`, `whatsapp.ts`, `formato.ts`. Probadas con Vitest. |
| `src/components/` | Partes de la página (`.astro`): encabezado, Arma tu pasta, secciones, platos, pie y hoja del pedido. |
| `src/scripts/` | `carta-interactiva.ts`: el único script del navegador. |
| `src/pages/index.astro` | La página: une los componentes. |

El mismo sitio sirve dos modos:

- **Domicilio** (`/`): carta, armado de pasta, pedido y envío por WhatsApp.
- **Mesa** (`/#mesa`): solo lectura, para el QR de las mesas.

### `shared/fixtures/`
Casos de prueba en JSON (por ejemplo, "fettuccine tinta + boloñesa + albóndigas = 32.500") que se ejecutan **en pytest y en Vitest**. Garantizan que Python y TypeScript calculen igual.

### `tools/pdf/`
Abre la versión de imprenta del sitio con Playwright y genera el PDF tabloide con sangrado, en CMYK.

## Flujo de build

```
menu.yaml ──► core: validar ──► core: exportar ──► carta.json + tipos.ts ──► web: astro build ──► dist/ ──► GitHub Pages
                                                                                         └──────────► tools/pdf ──► carta.pdf
```

En CI (GitHub Actions), cada *pull request* ejecuta: linter y pruebas de Python, chequeo de tipos y pruebas de TypeScript, y el build completo. Al fusionar en `main`, el sitio se publica.

## Evolución prevista

| Fase | Cambio en la arquitectura |
|---|---|
| 2 · Pedidos registrados | Se agrega `api/` (FastAPI) que reutiliza los modelos de `core/`, más PostgreSQL. La web envía el pedido a la API además de WhatsApp. **La API recalcula el precio**: nunca confía en el total que manda el navegador. |
| 3 · Automatización | Pasarela de pagos colombiana, WhatsApp Business Cloud API e integración con el POS si expone API. |
| 4 · IA | Pronóstico de demanda (series de tiempo sobre el historial de pedidos) para planear la producción diaria de pasta, y un asistente conversacional que usa *function calling* sobre la API de la carta. |

Cada fase se documenta con su propio ADR antes de construirse.
