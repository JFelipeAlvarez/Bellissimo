/**
 * ¿Está abierto el restaurante?
 * Espejo de core/src/bellissimo_core/horario.py; ambos cumplen
 * shared/fixtures/horario.json.
 *
 * El navegador sabe la hora en la zona del celular del cliente, que podría
 * no ser la de Bogotá. Por eso todo se convierte a la zona del restaurante
 * con Intl.DateTimeFormat, que trae la base de datos de zonas horarias.
 */
import type { Carta, Franja, Horario } from "../generated/tipos";

const DIAS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"] as const;
const CLAVES: readonly (keyof Horario)[] = [
  "lunes",
  "martes",
  "miercoles",
  "jueves",
  "viernes",
  "sabado",
  "domingo",
];

export interface EstadoAtencion {
  abierto: boolean;
  /** Hora de cierre de hoy ("20:00"), si está abierto. */
  cierra: string | null;
  /** Próxima apertura en ISO con la zona del restaurante, si está cerrado. */
  proximaApertura: string | null;
  /** Frase lista para mostrar. */
  texto: string;
}

export function estadoAtencion(carta: Carta, ahora: Date): EstadoAtencion {
  const zona = carta.restaurante.zona_horaria;
  const local = partesLocales(zona, ahora);
  const hoy = franjaDelDia(carta.horario, local.diaSemana);
  const segundos = local.hora * 3600 + local.minuto * 60 + local.segundo;

  if (hoy && segundosDe(hoy.abre) <= segundos && segundos < segundosDe(hoy.cierra)) {
    return {
      abierto: true,
      cierra: hoy.cierra.slice(0, 5),
      proximaApertura: null,
      texto: `Abierto · cierra a las ${hora12(hoy.cierra)}`,
    };
  }

  for (let dias = 0; dias < 8; dias++) {
    // Aritmética de calendario en UTC: sumar días a una fecha sin que la
    // zona horaria del navegador la desplace.
    const fecha = new Date(Date.UTC(local.anio, local.mes - 1, local.dia + dias));
    const diaSemana = (fecha.getUTCDay() + 6) % 7; // 0 = lunes, como en Python
    const franja = franjaDelDia(carta.horario, diaSemana);
    if (!franja || (dias === 0 && segundosDe(franja.abre) <= segundos)) continue;

    const cuando = dias === 0 ? "hoy" : dias === 1 ? "mañana" : `el ${DIAS[diaSemana]}`;
    return {
      abierto: false,
      cierra: null,
      proximaApertura: isoLocal(zona, fecha, franja.abre),
      texto: `Cerrado · abrimos ${cuando} a las ${hora12(franja.abre)}`,
    };
  }
  throw new Error("el horario no tiene ningún día abierto");
}

/** Día de la semana en la zona del restaurante: 0 = lunes … 6 = domingo. */
export function diaDeLaSemana(carta: Carta, ahora: Date): number {
  return partesLocales(carta.restaurante.zona_horaria, ahora).diaSemana;
}

export interface RenglonHorario {
  /** "Lunes y miércoles a sábado" */
  dias: string;
  /** "12:30 p. m. a 8:00 p. m." o "Cerrado" */
  horas: string;
  /** Días que cubre el renglón (0 = lunes), para resaltar el de hoy. */
  indices: number[];
}

/**
 * Agrupa los días que tienen el mismo horario, para mostrarlo corto:
 * "Lunes y miércoles a sábado · 12:30 p. m. a 8:00 p. m.". Los días
 * cerrados van al final.
 */
export function resumenHorario(horario: Horario): RenglonHorario[] {
  const grupos = new Map<string, { franja: Franja | null; indices: number[] }>();
  CLAVES.forEach((clave, i) => {
    const franja = horario[clave];
    const llave = franja ? `${franja.abre}-${franja.cierra}` : "cerrado";
    const grupo = grupos.get(llave) ?? { franja, indices: [] };
    grupo.indices.push(i);
    grupos.set(llave, grupo);
  });

  return [...grupos.values()]
    .sort((a, b) => Number(a.franja === null) - Number(b.franja === null))
    .map(({ franja, indices }) => ({
      dias: mayuscula(nombrarDias(indices)),
      horas: franja ? `${hora12(franja.abre)} a ${hora12(franja.cierra)}` : "Cerrado",
      indices,
    }));
}

/** [0, 2, 3, 4, 5] → "lunes y miércoles a sábado" */
function nombrarDias(indices: number[]): string {
  // Partir en tramos de días seguidos: [0], [2, 3, 4, 5].
  const tramos: number[][] = [];
  for (const i of indices) {
    const ultimo = tramos.at(-1);
    if (ultimo && ultimo.at(-1) === i - 1) ultimo.push(i);
    else tramos.push([i]);
  }
  const textos = tramos.flatMap((t) => {
    const [primero = 0] = t;
    const ultimo = t.at(-1) ?? primero;
    if (t.length === 1) return [DIAS[primero]];
    if (t.length === 2) return [DIAS[primero], DIAS[ultimo]];
    return [`${DIAS[primero]} a ${DIAS[ultimo]}`];
  });
  return textos.length === 1
    ? (textos[0] ?? "")
    : `${textos.slice(0, -1).join(", ")} y ${textos.at(-1) ?? ""}`;
}

function mayuscula(texto: string): string {
  return texto.charAt(0).toUpperCase() + texto.slice(1);
}

/** "20:00:00" → "8:00 p. m.", como se dice en Colombia. */
export function hora12(hora: string): string {
  const [h = 0, m = 0] = hora.split(":").map(Number);
  const sufijo = h < 12 ? "a. m." : "p. m.";
  return `${h % 12 || 12}:${String(m).padStart(2, "0")} ${sufijo}`;
}

// ── Detalles internos ───────────────────────────────────────────────────────

function franjaDelDia(horario: Horario, diaSemana: number): Franja | null {
  const clave = CLAVES[diaSemana];
  return clave ? horario[clave] : null;
}

function segundosDe(hora: string): number {
  const [h = 0, m = 0, s = 0] = hora.split(":").map(Number);
  return h * 3600 + m * 60 + s;
}

interface PartesLocales {
  anio: number;
  mes: number;
  dia: number;
  hora: number;
  minuto: number;
  segundo: number;
  diaSemana: number;
}

/** Fecha y hora de un instante, vistas en la zona indicada. */
function partesLocales(zona: string, instante: Date): PartesLocales {
  const partes = new Intl.DateTimeFormat("en-US", {
    timeZone: zona,
    hourCycle: "h23",
    year: "numeric",
    month: "numeric",
    day: "numeric",
    hour: "numeric",
    minute: "numeric",
    second: "numeric",
    weekday: "short",
  }).formatToParts(instante);
  const valor = (tipo: Intl.DateTimeFormatPartTypes): string =>
    partes.find((p) => p.type === tipo)?.value ?? "0";
  return {
    anio: Number(valor("year")),
    mes: Number(valor("month")),
    dia: Number(valor("day")),
    hora: Number(valor("hour")),
    minuto: Number(valor("minute")),
    segundo: Number(valor("second")),
    diaSemana: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"].indexOf(valor("weekday")),
  };
}

/** Diferencia de la zona con UTC en un instante: "-05:00". */
function desfase(zona: string, instante: Date): string {
  const nombre =
    new Intl.DateTimeFormat("en-US", { timeZone: zona, timeZoneName: "longOffset" })
      .formatToParts(instante)
      .find((p) => p.type === "timeZoneName")?.value ?? "GMT";
  return nombre === "GMT" ? "+00:00" : nombre.replace("GMT", "");
}

/** Fecha (en UTC de calendario) + hora local → "2026-10-21T12:30:00-05:00". */
function isoLocal(zona: string, fecha: Date, hora: string): string {
  const [h = 0, m = 0] = hora.split(":").map(Number);
  const dosDigitos = (n: number): string => String(n).padStart(2, "0");
  const aproximado = new Date(
    Date.UTC(fecha.getUTCFullYear(), fecha.getUTCMonth(), fecha.getUTCDate(), h, m),
  );
  return (
    `${fecha.getUTCFullYear()}-${dosDigitos(fecha.getUTCMonth() + 1)}-${dosDigitos(fecha.getUTCDate())}` +
    `T${dosDigitos(h)}:${dosDigitos(m)}:00${desfase(zona, aproximado)}`
  );
}
