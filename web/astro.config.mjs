// @ts-check
import { defineConfig } from "astro/config";

// El sitio se publica en GitHub Pages, bajo la ruta /bellissimo.
// Si más adelante se usa un dominio propio (por ejemplo bellissimo.com.co),
// basta con cambiar `site` y quitar `base`.
export default defineConfig({
  site: "https://jfelipealvarez.github.io",
  base: "/bellissimo",
  output: "static",
});
