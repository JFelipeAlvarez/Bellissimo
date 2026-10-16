# ADR 0003 · Sitio estático sin backend en la fase 1

- **Estado:** Aceptada
- **Fecha:** 2026-10-16

## Contexto

Los pedidos a domicilio llegan hoy por WhatsApp y los atiende una persona. En el local, los pedidos se toman en caja con el POS existente. No hay todavía necesidad de guardar pedidos ni de cobrar en línea.

## Decisión

En la fase 1 el sistema es un **sitio estático**: HTML, CSS y JavaScript generados en el build y servidos por **GitHub Pages**. El pedido se arma en el navegador y se envía como un mensaje prellenado de WhatsApp (`https://wa.me/<número>?text=...`).

No hay servidor, base de datos ni cuentas de usuario.

## Consecuencias

**Positivas**
- Costo de infraestructura: cero.
- Nada que administrar, parchar ni mantener encendido.
- El sitio carga muy rápido, incluso con mala señal.
- La publicación es automática desde GitHub.

**Negativas**
- Los pedidos no quedan registrados en ningún sistema, solo en el chat. Por eso todavía no hay datos para la fase 4 (IA).
- No se pueden cobrar pagos en línea.
- El total lo calcula el navegador. Es aceptable porque una persona confirma cada pedido en WhatsApp antes de prepararlo.

## Cuándo revisar esta decisión

Al empezar la fase 2: cuando el volumen de pedidos haga incómodo atenderlos solo por chat, o cuando se quiera empezar a acumular datos para el pronóstico de demanda.
