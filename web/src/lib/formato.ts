/**
 * Formato de valores para mostrar a las personas.
 * Espejo de core/src/bellissimo_core/formato.py.
 */

/** Pesos colombianos con punto de miles: 32500 → "$32.500". */
export function formatearPesos(valor: number): string {
  return "$" + String(valor).replace(/\B(?=(\d{3})+(?!\d))/g, ".");
}

/** Número de WhatsApp para mostrar: "573150336914" → "315 033 6914". */
export function formatearTelefono(numero: string): string {
  const local = numero.startsWith("57") ? numero.slice(2) : numero;
  return local.replace(/^(\d{3})(\d{3})(\d{4})$/, "$1 $2 $3");
}
