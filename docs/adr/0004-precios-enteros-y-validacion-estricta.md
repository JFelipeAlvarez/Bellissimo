# ADR 0004 · Precios como enteros y validación estricta de la carta

- **Estado:** Aceptada
- **Fecha:** 2026-10-16

## Contexto

`data/menu.yaml` lo editan personas, a mano. Los errores típicos al escribirlo son predecibles:

- Escribir un precio como `13.000` (con punto de miles) en lugar de `13000`.
- Equivocarse en el nombre de un campo (`precoi` en lugar de `precio`).
- Repetir un `id` al copiar y pegar un plato.
- Olvidar un día en el horario.

Además, el sistema hace sumas de dinero (el plato armado es pasta + salsa + proteína), y en la fase 2 esas sumas van a llegar a una base de datos y a una pasarela de pagos.

## Decisión

**1. Los precios son enteros en pesos colombianos.** Nunca `float`.

Los números decimales de las computadoras (`float`) no representan exactamente valores como `0.1`, así que en Python `0.1 + 0.2` da `0.30000000000000004`. Con plata eso produce centavos fantasma y totales que no cuadran. Como el peso colombiano no usa centavos en la práctica, un `int` representa cualquier precio de forma exacta. Además, el precio debe ser positivo, no mayor a $1.000.000 y múltiplo de 100.

Hay una trampa específica de YAML: `precio: 13.000` no es trece mil, es el número decimal **13,0**. Por eso el modelo rechaza cualquier precio que no llegue como entero, con un mensaje que explica cómo escribirlo (`13000`). Sin esa regla, Pydantic convertiría 13,0 en 13 y el error diría "debe ser múltiplo de 100", que no ayuda a encontrar el problema.

**2. La validación es estricta y falla temprano.** Los modelos de Pydantic:

- **Rechazan campos desconocidos** (`extra="forbid"`): un error de tipeo se reporta en lugar de ignorarse.
- **Exigen todos los días del horario**: un día olvidado es un error; un día cerrado se escribe explícitamente como `null`.
- **Exigen ids únicos en toda la carta**, con un formato fijo (`minusculas-con-guiones`). El id identifica al plato aunque su nombre cambie; en la fase 2 será la referencia en los pedidos guardados.
- **Son inmutables** (`frozen=True`): una vez cargada, ninguna parte del programa puede alterar la carta por accidente.

**3. Los errores se explican con su ubicación**, por ejemplo: `secciones → 2 → platos → 0 → precio: Input should be greater than 0`.

**4. El YAML se lee con `yaml.safe_load`**, que solo construye datos simples. `yaml.load` puede ejecutar código escondido en el archivo.

**5. La CI ejecuta `bellissimo validar`** en cada *pull request*: una carta inválida no puede llegar a `main`.

## Consecuencias

**Positivas**
- Los errores de edición se detectan antes de publicar, con un mensaje que dice dónde están.
- Las sumas de dinero son exactas.
- Los ids estables preparan la carta para guardar pedidos en la fase 2.

**Negativas**
- Agregar un campo nuevo a un plato exige actualizar el modelo; no basta con escribirlo en el YAML. Es intencional: cada dato nuevo es una decisión explícita.
- Los mensajes de error de Pydantic vienen en inglés. Los de nuestras reglas propias están en español; si molesta, se pueden traducir en `loader.py`.
