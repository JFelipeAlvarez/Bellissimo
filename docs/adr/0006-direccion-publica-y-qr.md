# ADR 0006 · La dirección pública la decide GitHub Pages y los QR salen de ella

- **Estado:** Aceptada
- **Fecha:** 2026-10-27

## Contexto

La carta se publica en GitHub Pages (ADR 0003). Su dirección depende del usuario, del **nombre exacto del repositorio** (hoy `Bellissimo`, con mayúscula) o de un dominio propio si algún día se compra uno (por ejemplo `bellissimo.com.co`).

Esa dirección se usa en tres lugares: en las rutas de la página (`/Bellissimo/_astro/…`), en los metadatos (vista previa al compartir el enlace) y en los **QR impresos** de las mesas y los domicilios. Si la dirección escrita en el código no coincide con la real, el sitio carga sin estilos o los QR llevan a una página de error, y un QR impreso no se puede corregir.

## Decisión

1. **La dirección no se escribe a mano.** El flujo `publicar.yml` le pregunta a GitHub Pages su dirección (`actions/configure-pages`) y se la pasa al build en `SITIO_URL`. `astro.config.mjs` saca de ella `site` y `base`.
2. **Los QR se generan en el build** (`/qr/`, con la librería `qrcode`) a partir de esa misma dirección. No se usa ningún servicio externo de QR: no hay cuentas, ni redirecciones de terceros que puedan caducar.
3. El QR de **mesa** apunta a la carta con `#mesa`; el de **domicilio**, a la carta sin nada más.
4. Los QR usan **corrección de errores nivel Q** (se leen aunque se dañe cerca del 25 %) y se imprimen en tinta oscura sobre blanco, a 5 cm.

## Consecuencias

**Positivas**
- Si el repositorio se renombra o se agrega un dominio propio, la página y los QR se ajustan solos en la siguiente publicación.
- La página `/qr/` muestra exactamente la dirección codificada, para revisarla antes de imprimir.

**Negativas**
- **Un QR impreso queda atado a la dirección del día en que se imprimió.** Si después cambia (renombrar el repositorio, pasar a un dominio propio), los QR viejos pueden dejar de funcionar y hay que reimprimirlos. Por eso, la dirección se decide **antes** de la primera impresión.
- En el computador local no existe `SITIO_URL`; se usa una dirección por defecto y la página `/qr/` advierte que no se imprima desde ahí.
