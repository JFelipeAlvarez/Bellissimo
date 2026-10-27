/**
 * Lo interactivo de la carta: armar la pasta, el pedido, el horario y el
 * envío por WhatsApp.
 *
 * Principio: el HTML ya trae toda la carta (lo generó Astro). Este script no
 * dibuja platos; solo escucha clics y actualiza textos. Los precios y los
 * nombres salen de las mismas funciones que se prueban con los casos
 * compartidos (src/lib), así que el total que ve el cliente es el mismo que
 * calcularía Python.
 */
import type { DatosEntrega, LineaArmado, LineaPlato } from "../generated/tipos";
import { carta } from "../lib/carta";
import { formatearPesos } from "../lib/formato";
import { diaDeLaSemana, estadoAtencion } from "../lib/horario";
import { CANTIDAD_MAXIMA, describirLinea, precioUnitario, subtotal, type Linea } from "../lib/pedido";
import { enlaceWhatsapp, mensajePedido } from "../lib/whatsapp";

// La "v1" permite cambiar el formato en el futuro sin leer datos viejos mal.
const CLAVE_PEDIDO = "bellissimo:pedido:v1";
const CLAVE_DATOS = "bellissimo:datos:v1";
const esMesa = document.documentElement.classList.contains("mode-mesa");

/** Busca un elemento que DEBE existir; si no está, el error dice cuál. */
function buscar<T extends Element = HTMLElement>(selector: string, dentro: ParentNode = document): T {
  const elemento = dentro.querySelector<T>(selector);
  if (!elemento) throw new Error(`No se encontró ${selector} en la página`);
  return elemento;
}

// ── Avisos cortos (toast) ───────────────────────────────────────────────────

const aviso = buscar("#aviso");
let temporizador: number | undefined;

function avisar(texto: string): void {
  aviso.textContent = texto;
  aviso.classList.add("show");
  window.clearTimeout(temporizador);
  temporizador = window.setTimeout(() => aviso.classList.remove("show"), 2200);
}

// ── Almacenamiento en el celular ────────────────────────────────────────────
// localStorage puede fallar (modo privado, almacenamiento lleno). Si falla,
// la página sigue funcionando; solo no recuerda el pedido al recargar.

function leer(clave: string): unknown {
  try {
    const texto = localStorage.getItem(clave);
    return texto ? JSON.parse(texto) : null;
  } catch {
    return null;
  }
}

function guardar(clave: string, valor: unknown): void {
  try {
    localStorage.setItem(clave, JSON.stringify(valor));
  } catch {
    // Sin almacenamiento: el pedido vive solo mientras la pestaña esté abierta.
  }
}

// ── El pedido ───────────────────────────────────────────────────────────────
// Se guardan solo ids y cantidades, nunca precios: el precio siempre se
// recalcula con la carta actual. Si mañana sube un precio, el pedido guardado
// muestra el nuevo; si un plato sale de la carta, su línea se descarta.

function esValida(linea: Linea): boolean {
  try {
    precioUnitario(carta, linea);
    return true;
  } catch {
    return false;
  }
}

function cargarPedido(): Linea[] {
  const guardado = leer(CLAVE_PEDIDO);
  return Array.isArray(guardado) ? (guardado as Linea[]).filter(esValida) : [];
}

const lineas: Linea[] = cargarPedido();

const cantidadDe = (linea: Linea): number => linea.cantidad ?? 1;

/** Dos líneas con la misma llave son el mismo producto: se suman. */
function llave(linea: Linea): string {
  return linea.tipo === "plato"
    ? `plato|${linea.id}|${linea.opcion ?? ""}`
    : `armado|${linea.pasta}|${linea.salsa ?? ""}|${linea.proteina ?? ""}`;
}

function agregar(nueva: Linea): void {
  const existente = lineas.find((l) => llave(l) === llave(nueva));
  if (existente && cantidadDe(existente) >= CANTIDAD_MAXIMA) {
    avisar(`Máximo ${CANTIDAD_MAXIMA} unidades por producto.`);
    return;
  }
  if (existente) existente.cantidad = cantidadDe(existente) + 1;
  else lineas.push({ ...nueva, cantidad: 1 });
  pedidoCambio();
  avisar(`Agregado: ${describirLinea(carta, nueva)}`);
}

function pedidoCambio(): void {
  guardar(CLAVE_PEDIDO, lineas);
  pintarPedido();
}

// ── Arma tu pasta ───────────────────────────────────────────────────────────

const armar = buscar<HTMLFormElement>("#armar");
const armarTotal = buscar("#armar-total");
const armarResumen = buscar("#armar-resumen");
const armarAgregar = buscar<HTMLButtonElement>("#armar-agregar");

/** Lo elegido en el formulario, o null si todavía no hay pasta. */
function lineaArmada(): LineaArmado | null {
  const datos = new FormData(armar);
  const valor = (campo: string): string => String(datos.get(campo) ?? "");
  if (!valor("pasta")) return null;
  const linea: LineaArmado = { tipo: "armado", pasta: valor("pasta") };
  if (valor("salsa")) linea.salsa = valor("salsa");
  if (valor("proteina")) linea.proteina = valor("proteina");
  return linea;
}

function pintarArmado(): void {
  const linea = lineaArmada();
  armarTotal.textContent = formatearPesos(linea ? precioUnitario(carta, linea) : 0);
  armarResumen.textContent = linea ? describirLinea(carta, linea) : "Empieza eligiendo tu pasta.";
  armarAgregar.disabled = linea === null;
}

armar.addEventListener("change", pintarArmado);
armar.addEventListener("submit", (evento) => {
  evento.preventDefault(); // sin esto, el navegador recargaría la página
  const linea = lineaArmada();
  if (!linea) return;
  agregar(linea);
  armar.reset(); // vuelve a "sin salsa" y "sin proteína"
  pintarArmado();
});

// Salsa (como adición) o proteína sola: el <select> ya trae el id.
const aparte = buscar<HTMLSelectElement>("#aparte-elegir");
buscar("#aparte-agregar").addEventListener("click", () => {
  agregar({ tipo: "plato", id: aparte.value });
});

// ── Platos de las secciones ─────────────────────────────────────────────────
// Un solo "escuchador" para todos los botones "Agregar" (delegación de
// eventos): más simple que poner uno en cada uno de los 50 platos.

document.addEventListener("click", (evento) => {
  if (!(evento.target instanceof Element)) return;
  const boton = evento.target.closest<HTMLButtonElement>("[data-agregar]");
  const id = boton?.dataset["agregar"];
  if (!boton || !id) return;

  const linea: LineaPlato = { tipo: "plato", id };
  const elegida = boton
    .closest("[data-plato]")
    ?.querySelector<HTMLInputElement>(`input[name="opcion-${CSS.escape(id)}"]:checked`);
  if (elegida) linea.opcion = elegida.value;
  agregar(linea);
});

// ── Hoja del pedido ─────────────────────────────────────────────────────────

const barra = buscar("#barra-pedido");
const barraCantidad = buscar("#barra-cantidad");
const barraTotal = buscar("#barra-total");
const hoja = buscar<HTMLDialogElement>("#pedido");
const vacio = buscar("#pedido-vacio");
const contenedorLineas = buscar("#lineas");
const totales = buscar("#totales");
const plantilla = buscar<HTMLTemplateElement>("#plantilla-linea");
const entrega = buscar<HTMLFormElement>("#entrega");
const enviar = buscar<HTMLAnchorElement>("#enviar");
const copiar = buscar<HTMLButtonElement>("#copiar");

function pintarPedido(): void {
  const unidades = lineas.reduce((suma, l) => suma + cantidadDe(l), 0);
  const total = lineas.length > 0 ? subtotal(carta, lineas) : 0;

  barra.hidden = esMesa || unidades === 0;
  barraCantidad.textContent = String(unidades);
  barraTotal.textContent = formatearPesos(total);
  buscar("#subtotal").textContent = formatearPesos(total);
  buscar("#total").textContent = formatearPesos(total);

  // "En tu pedido: 2" debajo de cada plato agregado.
  for (const marca of document.querySelectorAll<HTMLElement>("[data-en-pedido]")) {
    const n = lineas
      .filter((l) => l.tipo === "plato" && l.id === marca.dataset["enPedido"])
      .reduce((suma, l) => suma + cantidadDe(l), 0);
    marca.textContent = n > 0 ? `En tu pedido: ${n}` : "";
  }

  const estaVacio = lineas.length === 0;
  vacio.hidden = !estaVacio;
  totales.hidden = estaVacio;
  entrega.hidden = estaVacio;
  copiar.hidden = estaVacio;
  enviar.setAttribute("aria-disabled", String(estaVacio));

  contenedorLineas.replaceChildren(...lineas.map(filaDeLinea));
  actualizarEnlace();
}

/** Copia la <template> de Carrito.astro y llena sus textos. */
function filaDeLinea(linea: Linea, indice: number): HTMLElement {
  const fila = plantilla.content.firstElementChild?.cloneNode(true);
  if (!(fila instanceof HTMLElement)) throw new Error("La plantilla de línea está vacía");
  const nombre = describirLinea(carta, linea);
  const unitario = precioUnitario(carta, linea);

  fila.dataset["indice"] = String(indice);
  buscar(".line-name", fila).textContent = nombre;
  buscar(".line-total", fila).textContent = formatearPesos(unitario * cantidadDe(linea));
  buscar(".line-unit", fila).textContent = `${formatearPesos(unitario)} c/u`;
  buscar("output", fila).textContent = String(cantidadDe(linea));
  buscar('[data-accion="quitar"]', fila).setAttribute("aria-label", `Quitar uno: ${nombre}`);
  buscar('[data-accion="sumar"]', fila).setAttribute("aria-label", `Agregar uno: ${nombre}`);
  return fila;
}

contenedorLineas.addEventListener("click", (evento) => {
  if (!(evento.target instanceof Element)) return;
  const boton = evento.target.closest<HTMLButtonElement>("[data-accion]");
  const indice = Number(boton?.closest<HTMLElement>(".line")?.dataset["indice"]);
  const linea = lineas[indice];
  if (!boton || !linea) return;

  const accion = boton.dataset["accion"];
  if (accion === "sumar") {
    if (cantidadDe(linea) >= CANTIDAD_MAXIMA) return avisar(`Máximo ${CANTIDAD_MAXIMA} unidades.`);
    linea.cantidad = cantidadDe(linea) + 1;
  } else {
    linea.cantidad = cantidadDe(linea) - 1;
    if (linea.cantidad < 1) lineas.splice(indice, 1);
  }
  pedidoCambio();

  // Al redibujar, el botón tocado se reemplaza: devolvemos el foco al nuevo
  // para que quien navega con teclado o lector de pantalla no se pierda.
  const mismo = contenedorLineas.querySelector<HTMLElement>(
    `[data-indice="${indice}"] [data-accion="${accion}"]`,
  );
  (mismo ?? buscar<HTMLElement>("#cerrar-pedido")).focus();
});

buscar("#abrir-pedido").addEventListener("click", () => {
  pintarEstado();
  hoja.showModal();
});
buscar("#cerrar-pedido").addEventListener("click", () => hoja.close());
hoja.addEventListener("click", (evento) => {
  if (evento.target === hoja) hoja.close(); // clic en el fondo oscuro
});

// ── Datos de entrega y WhatsApp ─────────────────────────────────────────────

const obligatorios = ["nombre", "direccion", "barrio"] as const;

function datosEntrega(): DatosEntrega {
  const datos = new FormData(entrega);
  const texto = (campo: string): string => String(datos.get(campo) ?? "").trim();
  const pago = texto("pago") === "transferencia" ? "transferencia" : "efectivo";
  const pagaCon = Number(texto("paga_con").replace(/\D/g, "")); // "50.000" → 50000
  return {
    nombre: texto("nombre"),
    direccion: texto("direccion"),
    barrio: texto("barrio"),
    pago,
    paga_con: pago === "efectivo" && pagaCon > 0 ? pagaCon : null,
    notas: texto("notas") || null,
  };
}

function campo(nombre: string): HTMLInputElement {
  return buscar<HTMLInputElement>(`[name="${nombre}"]`, entrega);
}

function marcarError(nombre: string, hayError: boolean): void {
  campo(nombre).setAttribute("aria-invalid", String(hayError));
  buscar(`#e-${nombre}-err`).hidden = !hayError;
}

function validarEntrega(): boolean {
  const faltantes = obligatorios.filter((nombre) => !campo(nombre).value.trim());
  for (const nombre of obligatorios) marcarError(nombre, faltantes.includes(nombre));
  const [primero] = faltantes;
  if (primero) campo(primero).focus();
  return faltantes.length === 0;
}

function mensaje(): string {
  return mensajePedido(carta, lineas, datosEntrega());
}

function actualizarEnlace(): void {
  if (lineas.length > 0) enviar.href = enlaceWhatsapp(carta.restaurante.whatsapp, mensaje());
}

// Recordar nombre, dirección y barrio para el próximo pedido.
const recordados = leer(CLAVE_DATOS);
if (recordados && typeof recordados === "object") {
  for (const nombre of obligatorios) {
    const valor = (recordados as Record<string, unknown>)[nombre];
    if (typeof valor === "string") campo(nombre).value = valor;
  }
}

entrega.addEventListener("input", (evento) => {
  if (evento.target instanceof HTMLInputElement && evento.target.hasAttribute("aria-invalid")) {
    marcarError(evento.target.name, false);
  }
  const { nombre, direccion, barrio, pago } = datosEntrega();
  guardar(CLAVE_DATOS, { nombre, direccion, barrio });
  buscar("#campo-paga-con").hidden = pago !== "efectivo";
  actualizarEnlace();
});
entrega.addEventListener("submit", (evento) => evento.preventDefault());

enviar.addEventListener("click", (evento) => {
  if (lineas.length === 0 || !validarEntrega()) {
    evento.preventDefault();
    return;
  }
  actualizarEnlace();
  avisar("Abriendo WhatsApp…");
});

copiar.addEventListener("click", async () => {
  if (!validarEntrega()) return;
  const telefono = aviso.dataset["telefono"] ?? "";
  try {
    await navigator.clipboard.writeText(mensaje());
    avisar(`Pedido copiado. Pégalo en WhatsApp al ${telefono}.`);
  } catch {
    avisar(`No se pudo copiar. Escríbenos al ${telefono}.`);
  }
});

// ── Pestañas ────────────────────────────────────────────────────────────────

const pestanas = buscar("#pestanas");
const secciones = [...document.querySelectorAll<HTMLElement>("main section.menu")];

pestanas.addEventListener("click", (evento) => {
  if (!(evento.target instanceof Element)) return;
  const pestana = evento.target.closest<HTMLAnchorElement>(".tab");
  const destino = document.getElementById(pestana?.dataset["destino"] ?? "");
  if (!destino) return;
  // Sin esto, el enlace cambiaría la dirección a #horno y se perdería #mesa.
  evento.preventDefault();
  destino.scrollIntoView({ block: "start" });
});

let actual = "";
function marcarPestana(): void {
  // La sección activa es la última cuyo título ya pasó la barra de pestañas.
  const visible = secciones.filter((s) => s.getBoundingClientRect().top < 140).at(-1) ?? secciones[0];
  if (!visible || visible.id === actual) return;
  actual = visible.id;
  for (const pestana of pestanas.querySelectorAll<HTMLElement>(".tab")) {
    const activa = pestana.dataset["destino"] === actual;
    pestana.setAttribute("aria-current", String(activa));
    if (activa) pestanas.scrollTo({ left: pestana.offsetLeft - 16, behavior: "smooth" });
  }
}

let pendiente = false;
window.addEventListener(
  "scroll",
  () => {
    if (pendiente) return;
    pendiente = true; // como máximo una vez por cuadro de pantalla
    requestAnimationFrame(() => {
      pendiente = false;
      marcarPestana();
    });
  },
  { passive: true },
);

// ── ¿Abierto o cerrado? ─────────────────────────────────────────────────────

function pintarEstado(): void {
  const ahora = new Date();
  const estado = estadoAtencion(carta, ahora);
  const chip = buscar("#estado");
  chip.classList.toggle("open", estado.abierto);
  chip.classList.toggle("closed", !estado.abierto);
  buscar("#estado-texto").textContent = estado.texto;

  const hoy = String(diaDeLaSemana(carta, ahora));
  for (const dia of document.querySelectorAll<HTMLElement>("#horario dt")) {
    const esHoy = (dia.dataset["dias"] ?? "").split(",").includes(hoy);
    dia.classList.toggle("today", esHoy);
    dia.nextElementSibling?.classList.toggle("today", esHoy);
  }

  const avisoCerrado = buscar("#aviso-cerrado");
  avisoCerrado.hidden = estado.abierto;
  avisoCerrado.textContent =
    `Ahora estamos cerrados: ${estado.texto.replace(/^Cerrado · /, "")}. ` +
    "Puedes enviar tu pedido y te respondemos apenas abramos.";
}

// ── Arranque ────────────────────────────────────────────────────────────────

pintarEstado();
window.setInterval(pintarEstado, 60_000);
pintarArmado(); // el navegador puede restaurar radios marcados al volver atrás
pintarPedido();
marcarPestana();
