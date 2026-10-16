# ADR 0001 · La carta tiene una única fuente de verdad

- **Estado:** Aceptada
- **Fecha:** 2026-10-16

## Contexto

La carta de Bellissimo existe en varios formatos: el PDF para la imprenta, la carta web para domicilios y, más adelante, la que consulte un asistente de pedidos. En la versión inicial del proyecto, los precios estaban escritos a mano en cada uno.

Eso ya causó problemas: al agregar el salmón como proteína hubo que editarlo en dos archivos distintos, y es cuestión de tiempo que un precio quede distinto en la web y en la carta impresa. Un cliente que ve un precio en el celular y otro en la mesa pierde confianza.

## Decisión

La carta se define **una sola vez**, en `data/menu.yaml`. Ningún otro archivo del repositorio escribe precios, nombres ni descripciones de platos a mano.

- `core/` lee y valida el archivo con modelos Pydantic.
- Todas las salidas (web, modo mesa, PDF) se **generan** desde esos modelos.
- Si el archivo tiene un error (un precio negativo, un plato sin nombre, una sección duplicada), la validación falla y el build se detiene. Nada se publica con datos inválidos.

Se eligió YAML en lugar de JSON porque lo editan personas: admite comentarios y es más fácil de leer sin herramientas.

## Consecuencias

**Positivas**
- Cambiar un precio es cambiar una línea, y todas las salidas quedan consistentes.
- La carta tiene historial en Git: se sabe qué cambió, cuándo y quién lo cambió.
- La validación automática atrapa errores antes de que lleguen a los clientes.

**Negativas**
- Para ver un cambio hay que ejecutar el build. Se mitiga con CI: al fusionar el *pull request*, todo se regenera y publica solo.
- Editar YAML requiere cuidado con la indentación. Se mitiga con validación estricta y mensajes de error claros.
