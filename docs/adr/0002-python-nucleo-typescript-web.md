# ADR 0002 · Python para el núcleo, TypeScript para la web

- **Estado:** Aceptada
- **Fecha:** 2026-10-16

## Contexto

El proyecto necesita lógica de negocio (validar la carta, calcular precios, saber si el restaurante está abierto) y una interfaz web interactiva para celular. Las fases futuras incluyen una API de pedidos y modelos de IA (pronóstico de demanda, asistente conversacional).

## Decisión

- **Núcleo en Python** (`core/`), con Pydantic para los modelos. Es el ecosistema natural para las fases 2 (FastAPI usa Pydantic) y 4 (ciencia de datos e IA), así que los modelos que escribimos hoy se reutilizan sin cambios.
- **Web en TypeScript** (`web/`), con Astro. Los navegadores ejecutan JavaScript, y TypeScript agrega tipos que atrapan errores al compilar.
- **El contrato entre ambos se genera, no se copia.** `core/` exporta `menu.json` y un archivo de tipos TypeScript derivado del JSON Schema de los modelos Pydantic. Si un modelo cambia en Python, el frontend deja de compilar hasta que se actualice.
- **Las reglas de precio se prueban en los dos lenguajes** con los mismos casos (`shared/fixtures/`). El navegador calcula el total para mostrarlo; cuando exista la API (fase 2), el servidor lo recalcula y es la autoridad.

### Alternativas consideradas

| Alternativa | Por qué no |
|---|---|
| Todo en Python, con plantillas Jinja2 y JavaScript sin tipos | Menos piezas, pero la parte interactiva crece (carrito, armado de platos) y sin tipos se vuelve frágil. |
| Todo en TypeScript | Simplifica el build, pero aleja el proyecto del ecosistema de datos e IA de las fases 2 y 4. |
| Frontend como SPA (React) que pide la carta al cargar | La carta casi nunca cambia; generarla en build da páginas más rápidas, mejor SEO y cero servidor. |

## Consecuencias

- Hay dos gestores de dependencias: **uv** para Python y **npm** para TypeScript. La CI ejecuta ambos.
- El build tiene un orden fijo: primero `core` exporta, después `web` compila.
- Tener las mismas reglas en dos lenguajes tiene un costo, que se controla con los casos de prueba compartidos.
