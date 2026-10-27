/**
 * Pedidos y reglas de precio.
 * Espejo de core/src/bellissimo_core/pedido.py: las dos versiones cumplen
 * los casos de shared/fixtures/precios.json (ADR 0002).
 *
 * En el navegador, estas funciones calculan el total que ve el cliente.
 * Cuando exista la API (fase 2), el servidor recalculará el precio con la
 * versión de Python: nunca se confía en un total que manda el navegador.
 */
import type { Carta, LineaArmado, LineaPlato, Plato } from "../generated/tipos";

export type Linea = LineaPlato | LineaArmado;

export const CANTIDAD_MAXIMA = 50;

export type CodigoError =
  | "pedido_vacio"
  | "plato_inexistente"
  | "no_es_pasta"
  | "no_es_salsa"
  | "no_es_proteina"
  | "solo_en_arma_tu_pasta"
  | "falta_opcion"
  | "opcion_invalida"
  | "sin_opciones"
  | "cantidad_invalida";

export class PedidoInvalidoError extends Error {
  constructor(
    readonly codigo: CodigoError,
    mensaje: string,
  ) {
    super(mensaje);
    this.name = "PedidoInvalidoError";
  }
}

// ── Índice de la carta ──────────────────────────────────────────────────────
// Buscar un plato recorriendo toda la carta cada vez sería lento si se hace
// muchas veces. El índice se construye una vez por carta y se guarda en un
// WeakMap: si la carta deja de usarse, el navegador libera también su índice.

interface Indice {
  pastas: Map<string, Plato>;
  salsas: Map<string, Plato>;
  proteinas: Map<string, Plato>;
  /** Todo lo que se puede pedir suelto: secciones, proteínas y salsas (como adición). */
  sueltos: Map<string, Plato>;
}

const indices = new WeakMap<Carta, Indice>();

function porId(platos: Iterable<Plato>): Map<string, Plato> {
  return new Map(Array.from(platos, (p) => [p.id, p]));
}

function indice(carta: Carta): Indice {
  let idx = indices.get(carta);
  if (idx) return idx;
  const atp = carta.arma_tu_pasta;
  const pastas = porId(atp.pastas.flatMap((g) => g.platos));
  const salsas = porId(atp.salsas.flatMap((g) => g.platos));
  const proteinas = porId(atp.proteinas);
  const deSecciones = carta.secciones.flatMap((s) => [
    ...s.platos,
    ...s.grupos.flatMap((g) => g.platos),
  ]);
  const sueltos = porId([...deSecciones, ...proteinas.values(), ...salsas.values()]);
  idx = { pastas, salsas, proteinas, sueltos };
  indices.set(carta, idx);
  return idx;
}

// ── Reglas ──────────────────────────────────────────────────────────────────

/** Precio de UNA unidad de la línea. Lanza `PedidoInvalidoError` si no es válida. */
export function precioUnitario(carta: Carta, linea: Linea): number {
  validarCantidad(linea.cantidad ?? 1);
  return linea.tipo === "armado" ? precioArmado(carta, linea) : platoSuelto(carta, linea).precio;
}

/** Suma de todas las líneas (precio unitario × cantidad), sin domicilio. */
export function subtotal(carta: Carta, lineas: readonly Linea[]): number {
  if (lineas.length === 0) {
    throw new PedidoInvalidoError("pedido_vacio", "el pedido no tiene productos");
  }
  return lineas.reduce((total, l) => total + precioUnitario(carta, l) * (l.cantidad ?? 1), 0);
}

/** Nombre legible de la línea, igual al de Python. */
export function describirLinea(carta: Carta, linea: Linea): string {
  precioUnitario(carta, linea); // valida antes de describir
  const idx = indice(carta);

  if (linea.tipo === "plato") {
    const plato = idx.sueltos.get(linea.id)!;
    if (idx.salsas.has(linea.id)) return `Adición de salsa ${plato.nombre}`;
    return linea.opcion ? `${plato.nombre} (${linea.opcion})` : plato.nombre;
  }

  let texto = idx.pastas.get(linea.pasta)!.nombre;
  texto += linea.salsa ? ` con salsa ${idx.salsas.get(linea.salsa)!.nombre}` : ", sin salsa";
  if (linea.proteina) texto += ` + ${idx.proteinas.get(linea.proteina)!.nombre}`;
  return texto;
}

// ── Detalles internos ───────────────────────────────────────────────────────

function validarCantidad(cantidad: number): void {
  if (!Number.isInteger(cantidad) || cantidad < 1 || cantidad > CANTIDAD_MAXIMA) {
    throw new PedidoInvalidoError(
      "cantidad_invalida",
      `la cantidad debe estar entre 1 y ${CANTIDAD_MAXIMA}`,
    );
  }
}

function precioArmado(carta: Carta, linea: LineaArmado): number {
  const { pastas, salsas, proteinas } = indice(carta);

  const pasta = pastas.get(linea.pasta);
  if (!pasta) {
    throw new PedidoInvalidoError("no_es_pasta", `'${linea.pasta}' no es una pasta de la carta`);
  }
  let total = pasta.precio;

  if (linea.salsa != null) {
    const salsa = salsas.get(linea.salsa);
    if (!salsa) {
      throw new PedidoInvalidoError("no_es_salsa", `'${linea.salsa}' no es una salsa de la carta`);
    }
    total += salsa.precio;
  }

  if (linea.proteina != null) {
    const proteina = proteinas.get(linea.proteina);
    if (!proteina) {
      throw new PedidoInvalidoError(
        "no_es_proteina",
        `'${linea.proteina}' no es una proteína de la carta`,
      );
    }
    total += proteina.precio;
  }

  return total;
}

function platoSuelto(carta: Carta, linea: LineaPlato): Plato {
  const { sueltos, pastas } = indice(carta);
  const plato = sueltos.get(linea.id);

  if (!plato) {
    if (pastas.has(linea.id)) {
      throw new PedidoInvalidoError(
        "solo_en_arma_tu_pasta",
        `'${linea.id}' es una pasta: se pide con Arma tu pasta, aunque sea sin salsa`,
      );
    }
    throw new PedidoInvalidoError("plato_inexistente", `'${linea.id}' no existe en la carta`);
  }

  const { opciones } = plato;
  if (opciones.length > 0) {
    if (linea.opcion == null) {
      throw new PedidoInvalidoError(
        "falta_opcion",
        `elige una opción para ${plato.nombre}: ${opciones.join(", ")}`,
      );
    }
    if (!opciones.includes(linea.opcion)) {
      throw new PedidoInvalidoError(
        "opcion_invalida",
        `'${linea.opcion}' no es una opción de ${plato.nombre}`,
      );
    }
  } else if (linea.opcion != null) {
    throw new PedidoInvalidoError("sin_opciones", `${plato.nombre} no tiene opciones para elegir`);
  }

  return plato;
}
