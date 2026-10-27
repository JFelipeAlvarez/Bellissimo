/**
 * Mensaje de pedido para WhatsApp.
 * Espejo de core/src/bellissimo_core/whatsapp.py; ambos cumplen
 * shared/fixtures/whatsapp.json carácter por carácter.
 */
import type { Carta, DatosEntrega } from "../generated/tipos";
import { formatearPesos } from "./formato";
import { describirLinea, precioUnitario, subtotal, type Linea } from "./pedido";

export function mensajePedido(
  carta: Carta,
  lineas: readonly Linea[],
  entrega: DatosEntrega,
): string {
  const renglones = [`Hola ${carta.restaurante.nombre}, quiero hacer un pedido a domicilio:`, ""];

  for (const linea of lineas) {
    const cantidad = linea.cantidad ?? 1;
    const total = precioUnitario(carta, linea) * cantidad;
    renglones.push(`• ${cantidad} x ${describirLinea(carta, linea)} = ${formatearPesos(total)}`);
  }

  renglones.push(
    "",
    `Subtotal: ${formatearPesos(subtotal(carta, lineas))} (más domicilio)`,
    "",
    `Nombre: ${entrega.nombre}`,
    `Dirección: ${entrega.direccion}`,
    `Barrio: ${entrega.barrio}`,
    `Pago: ${textoPago(entrega)}`,
  );
  if (entrega.notas) renglones.push(`Notas: ${entrega.notas}`);

  return renglones.join("\n");
}

/** Enlace que abre WhatsApp con el mensaje ya escrito. */
export function enlaceWhatsapp(numero: string, mensaje: string): string {
  return `https://wa.me/${numero}?text=${encodeURIComponent(mensaje)}`;
}

function textoPago(entrega: DatosEntrega): string {
  if (entrega.pago === "transferencia") return "Transferencia";
  if (entrega.paga_con) return `Efectivo, pago con ${formatearPesos(entrega.paga_con)}`;
  return "Efectivo";
}
