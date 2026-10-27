# shared/fixtures/

Casos de prueba en JSON que cumplen **tanto Python (pytest) como TypeScript (Vitest)**. Son el contrato entre los dos lenguajes ([ADR 0002](../../docs/adr/0002-python-nucleo-typescript-web.md)): si una de las dos versiones calcula distinto, su prueba falla.

| Archivo | Qué define |
|---|---|
| `carta.json` | Una carta pequeña y fija. Los casos usan esta carta, no la real, para que cambiar un precio en `data/menu.yaml` no rompa las pruebas de las reglas. |
| `precios.json` | Formato de pesos, precios de pedidos válidos y los **códigos de error** de los inválidos (`no_es_pasta`, `falta_opcion`…). |
| `horario.json` | Si el restaurante está abierto en un momento dado, cuándo vuelve a abrir y el texto que se muestra. Incluye casos en UTC. |
| `whatsapp.json` | El texto exacto del mensaje del pedido y su enlace `wa.me`. |

## Cómo agregar un caso

1. Agrega el objeto al arreglo `casos` (o `invalidos`) del archivo, con una `descripcion` clara: esa descripción es el nombre de la prueba.
2. Corre `uv run pytest` en `core/` (y `npm test` en `web/`, desde la sesión 4).
3. Si el caso describe una regla nueva, primero falla. Implementa la regla en los dos lenguajes hasta que pase. Eso es TDD.

Los errores se comparan por **código** y no por mensaje: el mensaje es para personas y puede cambiar de redacción o de idioma; el código no.
