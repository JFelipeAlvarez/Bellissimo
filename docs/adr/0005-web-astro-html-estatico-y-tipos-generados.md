# ADR 0005 · Web en Astro: HTML generado, un solo script y tipos generados

- **Estado:** Aceptada
- **Fecha:** 2026-10-27

## Contexto

La carta web tiene dos usos: pedir a domicilio (interactivo) y consultar en la mesa con el QR (solo lectura). La mayoría de la página es texto que cambia pocas veces al mes; lo interactivo es poco: armar la pasta, el pedido, el formulario y el enlace de WhatsApp.

El ADR 0002 decidió que Python define los modelos y TypeScript los consume. Falta decidir **cómo** se construye la página y **cómo** llegan los tipos a TypeScript.

## Decisión

1. **Todo el HTML se genera en el build con componentes `.astro`**, a partir de `carta.json`. El celular recibe la carta ya escrita; no la dibuja con JavaScript.
2. **Lo interactivo es un solo script en TypeScript sin framework** (`src/scripts/carta-interactiva.ts`): escucha clics y cambia textos. No se usa React, Vue ni Preact.
3. **Las reglas del navegador son las mismas funciones probadas** (`src/lib/`), espejo de `core/` y verificadas con `shared/fixtures/`. El script no calcula precios por su cuenta.
4. **Los tipos se generan**: `bellissimo exportar` escribe el JSON Schema de los modelos Pydantic, y `json-schema-to-typescript` lo convierte en `src/generated/tipos.ts`. En el esquema de la carta, los campos con valor por defecto son obligatorios (`json_schema_serialization_defaults_required`): `carta.json` siempre los trae.
5. **Los archivos generados no se suben a Git.** `npm run generar` los crea, y corre solo antes de `dev`, `build` y `test`.
6. **La carta de prueba también pasa por el exportador** (`npm run generar:prueba`), para que Vitest use la carta en el mismo formato que la real.
7. **El pedido guardado en el celular (`localStorage`) contiene solo ids y cantidades, nunca precios.** El precio se recalcula siempre con la carta vigente; si un plato sale de la carta, su línea se descarta al cargar.

### Alternativas consideradas

| Alternativa | Por qué no |
|---|---|
| React o Preact para el carrito y el armado | Agrega ~40 KB y un modelo mental nuevo para muy poca interactividad. El script actual pesa ~20 KB **con** la carta incluida. Si la interacción crece (fase 2: seguimiento del pedido), se puede agregar una "isla" de Astro sin rehacer la página. |
| Dibujar la carta con JavaScript en el navegador (como el prototipo) | Página en blanco si el script falla, peor para buscadores y más lenta con mala señal. |
| Escribir los tipos de TypeScript a mano | Se desincronizan en silencio. Generados, un cambio en Python hace fallar `astro check`. |
| Subir los archivos generados a Git | Diffs ruidosos y el riesgo de editar a mano algo que se sobreescribe. |

## Consecuencias

**Positivas**
- La carta se lee aunque el JavaScript no cargue; el modo mesa casi no lo necesita.
- Un cambio en los modelos de Python se propaga solo hasta el editor de TypeScript.
- Un pedido viejo guardado en el celular nunca muestra precios desactualizados.

**Negativas**
- Para trabajar en `web/` también hace falta **uv** (el paso `generar` llama a Python). La CI instala ambos.
- El script manipula el DOM a mano. Se mitiga con `<template>` (el HTML de cada fila vive en `Carrito.astro`) y con `buscar()`, que falla con un mensaje claro si falta un elemento.
