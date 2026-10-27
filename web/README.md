# bellissimo-web

Carta web de Bellissimo, hecha con [Astro](https://astro.build/) y TypeScript.

Genera HTML estático a partir de los datos que exporta `core/`. Solo lo interactivo (armar la pasta, el pedido) usa JavaScript en el navegador. Ver [`docs/ARCHITECTURE.md`](../docs/ARCHITECTURE.md) y el [ADR 0005](../docs/adr/0005-web-astro-html-estatico-y-tipos-generados.md).

## Comandos

```bash
npm ci            # instala las versiones exactas del package-lock.json
npm test          # pruebas de las reglas (Vitest) con los casos de shared/fixtures
npm run dev       # servidor local en http://localhost:4321/bellissimo/
npm run check     # chequeo de tipos
npm run build     # chequeo de tipos + build de producción en dist/
npm run preview   # sirve el build de producción localmente
npm run generar   # vuelve a generar src/generated/ (dev, build y test lo hacen solos)
```

Todos necesitan **uv** instalado: `generar` le pide a Python que exporte la carta.

Las **tarjetas QR** para imprimir están en `/qr/` (por ejemplo `http://localhost:4321/bellissimo/qr/`). Imprímelas siempre desde la carta **publicada**: en tu computador los QR apuntan a una dirección por defecto.

Para ver la carta en **modo mesa** (solo lectura, la del QR), agrega `#mesa` al final de la dirección: `http://localhost:4321/bellissimo/#mesa`.

## Carpetas

| Carpeta | Qué hay |
|---|---|
| `src/generated/` | Archivos generados desde `core/`. No se editan ni se suben a Git. |
| `src/lib/` | Reglas en TypeScript (precios, horario, WhatsApp), espejo de `core/`, con sus pruebas `*.test.ts`. |
| `src/components/` | Partes de la página. |
| `src/scripts/` | El script del navegador. |
| `src/styles/global.css` | Estilos y colores (modo claro y oscuro). |
| `public/` | Logo e íconos, se copian tal cual. |

## Instalar un paquete nuevo

`npm ci` funciona con el npm que trae Node 22, pero **instalar** un paquete nuevo con npm 10 puede fallar con `Cannot read properties of null (reading 'edgesOut')`. Usa npm 11:

```bash
npx -y npm@11 install --save-exact nombre-del-paquete
```
