// @ts-check
import { defineConfig } from "astro/config";

// Dirección pública de la carta (ADR 0006).
//
// Al publicar, GitHub Actions pregunta a GitHub Pages cuál es la dirección
// real del sitio y la pasa en SITIO_URL (ver .github/workflows/publicar.yml).
// Así no se escribe a mano: si el repositorio cambia de nombre o se usa un
// dominio propio (bellissimo.com.co), la página y los QR se ajustan solos.
//
// En tu computador no existe SITIO_URL y se usa el valor por defecto.
const sitio = new URL(process.env.SITIO_URL ?? "https://jfelipealvarez.github.io/bellissimo");

export default defineConfig({
  site: sitio.origin,
  base: sitio.pathname,
  output: "static",
});
