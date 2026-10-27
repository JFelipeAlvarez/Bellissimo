/**
 * Ayudas de presentación que solo usa la web (no tienen espejo en Python).
 */
import { describe, expect, it } from "vitest";
import type { Horario } from "../generated/tipos";
import { formatearTelefono } from "./formato";
import { hora12, resumenHorario } from "./horario";

const tarde = { abre: "12:30:00", cierra: "20:00:00" };

describe("resumenHorario", () => {
  it("agrupa los días con el mismo horario y deja los cerrados al final", () => {
    const horario: Horario = {
      lunes: tarde,
      martes: null,
      miercoles: tarde,
      jueves: tarde,
      viernes: tarde,
      sabado: tarde,
      domingo: { abre: "12:30:00", cierra: "19:00:00" },
    };
    expect(resumenHorario(horario)).toEqual([
      { dias: "Lunes y miércoles a sábado", horas: "12:30 p. m. a 8:00 p. m.", indices: [0, 2, 3, 4, 5] },
      { dias: "Domingo", horas: "12:30 p. m. a 7:00 p. m.", indices: [6] },
      { dias: "Martes", horas: "Cerrado", indices: [1] },
    ]);
  });

  it("nombra dos días seguidos con 'y' y toda la semana como un tramo", () => {
    const horario: Horario = {
      lunes: tarde,
      martes: tarde,
      miercoles: tarde,
      jueves: tarde,
      viernes: tarde,
      sabado: null,
      domingo: null,
    };
    expect(resumenHorario(horario).map((r) => r.dias)).toEqual([
      "Lunes a viernes",
      "Sábado y domingo",
    ]);
  });
});

describe("hora12", () => {
  it.each([
    ["00:15:00", "12:15 a. m."],
    ["09:05:00", "9:05 a. m."],
    ["12:30:00", "12:30 p. m."],
    ["20:00:00", "8:00 p. m."],
  ])("%s → %s", (hora, esperado) => {
    expect(hora12(hora)).toBe(esperado);
  });
});

describe("formatearTelefono", () => {
  it("quita el indicativo y agrupa como se lee en Colombia", () => {
    expect(formatearTelefono("573150336914")).toBe("315 033 6914");
  });
});
