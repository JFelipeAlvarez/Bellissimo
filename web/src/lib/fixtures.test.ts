/**
 * Casos compartidos con Python (shared/fixtures/).
 *
 * Son los MISMOS archivos que ejecuta core/tests/test_fixtures_compartidos.py.
 * Si esta prueba y la de Python pasan, las dos versiones de las reglas
 * calculan exactamente igual (ADR 0002).
 */
import { describe, expect, it } from "vitest";
import type { Carta, DatosEntrega } from "../generated/tipos";
import { formatearPesos } from "./formato";
import { estadoAtencion } from "./horario";
import { PedidoInvalidoError, precioUnitario, subtotal, type Linea } from "./pedido";
import { enlaceWhatsapp, mensajePedido } from "./whatsapp";
import datosCarta from "../generated/prueba/carta.json";
import datosHorario from "../../../shared/fixtures/horario.json";
import datosPrecios from "../../../shared/fixtures/precios.json";
import datosWhatsapp from "../../../shared/fixtures/whatsapp.json";

// La carta de prueba es shared/fixtures/carta.json pasada por el exportador
// de Python (`npm run generar:prueba`): llega igual que llega la carta real.
const carta = datosCarta as Carta;

/**
 * Los JSON importados traen el tipo que TypeScript adivina (por ejemplo,
 * `(string | number)[][]` en vez de `[number, string][]`). Esta función le
 * dice "confía en mí": la forma de los casos ya la usa también pytest.
 */
function tipar<T>(json: unknown): T {
  return json as T;
}

interface Caso {
  descripcion: string;
}

const precios = tipar<{
  formato_pesos: [number, string][];
  casos: (Caso & { lineas: Linea[]; precios_unitarios: number[]; subtotal: number })[];
  invalidos: (Caso & { lineas: Linea[]; codigo: string })[];
}>(datosPrecios);

const horario = tipar<{
  casos: (Caso & {
    ahora: string;
    abierto: boolean;
    cierra: string | null;
    proxima_apertura: string | null;
    texto: string;
  })[];
}>(datosHorario);

const whatsapp = tipar<{
  casos: (Caso & {
    lineas: Linea[];
    entrega: DatosEntrega;
    mensaje: string;
    enlace: string | null;
  })[];
}>(datosWhatsapp);

describe("precios", () => {
  it.each(precios.formato_pesos)("formatea %i como %s", (valor, esperado) => {
    expect(formatearPesos(valor)).toBe(esperado);
  });

  it.each(precios.casos)("$descripcion", (caso) => {
    expect(caso.lineas.map((l) => precioUnitario(carta, l))).toEqual(caso.precios_unitarios);
    expect(subtotal(carta, caso.lineas)).toBe(caso.subtotal);
  });

  it.each(precios.invalidos)("rechaza: $descripcion", (caso) => {
    let error: unknown;
    try {
      subtotal(carta, caso.lineas);
    } catch (e) {
      error = e;
    }
    expect(error).toBeInstanceOf(PedidoInvalidoError);
    expect((error as PedidoInvalidoError).codigo).toBe(caso.codigo);
  });
});

describe("horario", () => {
  it.each(horario.casos)("$descripcion", (caso) => {
    const estado = estadoAtencion(carta, new Date(caso.ahora));
    expect(estado.abierto).toBe(caso.abierto);
    expect(estado.cierra).toBe(caso.cierra);
    expect(estado.proximaApertura).toBe(caso.proxima_apertura);
    expect(estado.texto).toBe(caso.texto);
  });
});

describe("whatsapp", () => {
  it.each(whatsapp.casos)("$descripcion", (caso) => {
    const mensaje = mensajePedido(carta, caso.lineas, caso.entrega);
    expect(mensaje).toBe(caso.mensaje);
    if (caso.enlace !== null) {
      expect(enlaceWhatsapp(carta.restaurante.whatsapp, mensaje)).toBe(caso.enlace);
    }
  });
});
