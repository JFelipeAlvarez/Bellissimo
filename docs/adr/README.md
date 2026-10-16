# Registros de decisiones de arquitectura (ADR)

Un ADR (*Architecture Decision Record*) es un documento corto que registra **una** decisión importante: el contexto, lo que se decidió y sus consecuencias. Sirve para que dentro de seis meses (o en una entrevista) se pueda explicar por qué el sistema es como es.

Reglas:

- Se numeran en orden y no se borran. Si una decisión cambia, se escribe un ADR nuevo que la reemplaza y el viejo se marca como **Reemplazada por ADR XXXX**.
- Se escriben **antes** de implementar el cambio y se revisan en el mismo *pull request*.

| ADR | Decisión | Estado |
|---|---|---|
| [0001](0001-fuente-unica-de-verdad.md) | La carta tiene una única fuente de verdad | Aceptada |
| [0002](0002-python-nucleo-typescript-web.md) | Python para el núcleo, TypeScript para la web | Aceptada |
| [0003](0003-sitio-estatico-sin-backend.md) | Sitio estático sin backend en la fase 1 | Aceptada |

## Plantilla

```markdown
# ADR NNNN · Título en forma de decisión

- **Estado:** Propuesta | Aceptada | Reemplazada por ADR XXXX
- **Fecha:** AAAA-MM-DD

## Contexto
Qué problema hay y qué restricciones existen.

## Decisión
Qué se decidió, en términos concretos.

## Consecuencias
Qué mejora, qué empeora y cómo se mitiga.
```
