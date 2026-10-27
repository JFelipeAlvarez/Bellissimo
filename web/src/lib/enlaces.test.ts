import { describe, expect, it } from "vitest";
import { urlCarta } from "./enlaces";

describe("urlCarta", () => {
  it("arma la dirección de GitHub Pages con barra final", () => {
    expect(urlCarta("https://jfelipealvarez.github.io", "/Bellissimo")).toBe(
      "https://jfelipealvarez.github.io/Bellissimo/",
    );
    expect(urlCarta("https://jfelipealvarez.github.io", "/Bellissimo/")).toBe(
      "https://jfelipealvarez.github.io/Bellissimo/",
    );
  });

  it("agrega #mesa para el QR de las mesas", () => {
    expect(urlCarta("https://jfelipealvarez.github.io", "/bellissimo", "mesa")).toBe(
      "https://jfelipealvarez.github.io/bellissimo/#mesa",
    );
  });

  it("funciona con un dominio propio, sin subcarpeta", () => {
    expect(urlCarta("https://bellissimo.com.co", "/", "mesa")).toBe(
      "https://bellissimo.com.co/#mesa",
    );
  });
});
