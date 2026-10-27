/**
 * La carta, tal como la exportó core/ (`npm run generar`).
 *
 * Se usa en dos lugares:
 * - En los componentes .astro, al construir el HTML (en tu computador o en
 *   GitHub Actions, nunca en el celular del cliente).
 * - En el script del navegador, para calcular precios y armar el mensaje.
 *
 * El `as Carta` le dice a TypeScript que confíe en la forma del JSON. Es
 * seguro porque Python ya validó la carta antes de exportarla (ADR 0002).
 */
import datos from "../generated/carta.json";
import type { Carta } from "../generated/tipos";

export const carta = datos as Carta;
