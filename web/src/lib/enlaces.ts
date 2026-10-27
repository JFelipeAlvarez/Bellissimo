/**
 * Direcciones públicas de la carta.
 *
 * La dirección la decide GitHub Pages al publicar (ver astro.config.mjs y
 * ADR 0006). Aquí solo se arma, a partir de `site` y `base`, para no repetir
 * la lógica en la página, en los metadatos y en los QR.
 */

export type Modo = "domicilio" | "mesa";

/**
 * "https://x.github.io" + "/Bellissimo" → "https://x.github.io/Bellissimo/"
 * Con modo "mesa" agrega "#mesa": la misma página, sin botones de pedido.
 */
export function urlCarta(sitio: URL | string, base: string, modo: Modo = "domicilio"): string {
  const ruta = base.endsWith("/") ? base : `${base}/`;
  const url = new URL(ruta, sitio);
  if (modo === "mesa") url.hash = "mesa";
  return url.href;
}
