# bellissimo-web

Carta web de Bellissimo, hecha con [Astro](https://astro.build/) y TypeScript.

Genera HTML estático a partir de los datos que exporta `core/`. Solo lo interactivo (armar la pasta, el carrito) usa JavaScript en el navegador. Ver [`docs/ARCHITECTURE.md`](../docs/ARCHITECTURE.md).

## Comandos

```bash
npm ci            # instala las versiones exactas del package-lock.json
npm run dev       # servidor local en http://localhost:4321/bellissimo
npm run check     # chequeo de tipos
npm run build     # chequeo de tipos + build de producción en dist/
npm run preview   # sirve el build de producción localmente
```
