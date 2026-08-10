# 02. Matriz de simulaciones

## Criterios

- `C/U` significa que el mismo escenario se ejecutó tanto para Colegios como para Universidades.
- Las distribuciones muestran los tamaños reales de los grupos.
- `P1` y `P2` significan Purgatorio 1 y Purgatorio 2.
- La matriz automática comprobó asignación completa, ausencia de duplicados, separación de categorías, diferencia máxima de un participante entre grupos y ausencia de grupos unitarios evitables.
- Con 2 o 3 participantes el resultado correcto es detener explícitamente el modo automático. El sistema no fabrica grupos, byes ni clasificaciones ficticias.
- En las llaves automáticas solo se usan totales directos de 4, 8, 16 o 32. Los excedentes juegan rondas grupales/campales progresivas; nadie recibe un pase silencioso.

## Matriz de cantidades

| ID | Categoría | Participantes | Grupos / distribución | Repechaje | Resultado esperado | Resultado real | Estado |
| -- | --------- | ------------: | --------------------- | ---------- | ------------------ | -------------- | ------ |
| M01 | C/U | 2 | 0 | No | Modo mínimo pendiente; no crear grupos inválidos | `minimum_pending`, 0 clasificados | OK |
| M02 | C/U | 3 | 0 | No | Modo mínimo pendiente; no crear byes | `minimum_pending`, 0 clasificados | OK |
| M03 | C/U | 4 | 2: 2-2 | No | 4 clasificados; semifinal | 4 asignados y 4 clasificados | OK |
| M04 | C/U | 5 | 2: 3-2 | No | 4 clasificados; semifinal | Reparto completo 3-2 | OK |
| M05 | C/U | 6 | 2: 3-3 | No | 4 clasificados; semifinal | Reparto completo 3-3 | OK |
| M06 | C/U | 7 | 2: 4-3 | No | 4 clasificados; semifinal | Reparto completo 4-3 | OK |
| M07 | C/U | 8 | 2: 4-4 | No | 4 clasificados; semifinal | Reparto completo 4-4 | OK |
| M08 | C/U | 9 | 2: 5-4 | No | 4 clasificados; semifinal | Reparto completo 5-4 | OK |
| M09 | C/U | 10 | 2: 5-5 | No | 4 clasificados; semifinal | Reparto completo 5-5 | OK |
| M10 | C/U | 12 | 2: 6-6 | No | 4 clasificados; semifinal | Reparto completo 6-6 | OK |
| M11 | C/U | 16 | 4: 4-4-4-4 | No | 8 clasificados; cuartos | 16 asignados, 8 clasificados | OK |
| M12 | C/U | 17 | 4: 5-4-4-4 | No | 8 clasificados; progresión sin byes | Torneo completo y podio válido | OK |
| M13 | C/U | 24 | 4: 6-6-6-6 | No | 8 clasificados; cuartos | 24 asignados, 8 clasificados | OK |
| M14 | C/U | 31 | 4: 8-8-8-7 | No | 8 clasificados; cuartos | Reparto completo, diferencia máxima 1 | OK |
| M15 | C/U | 32 | 8: 4-4-4-4-4-4-4-4 | P1 habilitable | 16 clasificados; cuadro válido | Sin faltantes ni duplicados | OK |
| M16 | C/U | 33 | 8: 5-4-4-4-4-4-4-4 | P1 habilitable | 16 clasificados; excedente juega | Torneo completo y podio válido | OK |
| M17 | C/U | 40 | 8: 5-5-5-5-5-5-5-5 | P1 habilitable | 16 clasificados; repechaje coherente | Flujos con 0, 1 y 2 repechajes validados | OK |
| M18 | C/U | 73 | 16: 9×5 y 7×4 | P1 habilitable | 32 clasificados; ronda de 32 | 73 asignados exactamente una vez | OK |

La cantidad alta razonable usada fue 73, que coincide con la competencia real de Colegios.

## Simulaciones integrales

| ID | Categoría | Participantes | Motor | Repechaje | Recorrido validado | Resultado |
| --- | --------- | ------------: | ----- | ---------- | ------------------ | --------- |
| F01 | Colegios | 5 | Progresivo | 0 | Grupos → semifinal → final + tercer lugar → podio | Completado |
| F02 | Universidades | 16 | Progresivo | 0 | Grupos → cuartos → semifinal → final + tercer lugar → podio | Completado |
| F03 | Ambas simultáneas | 9 / 10 | Progresivo | 0 | Dos competencias independientes hasta podio | Ambas completadas |
| F04 | Universidades | 16 | Heredado | 0 | Batallas precreadas hasta podio | Completado |
| F05 | Universidades | 40 | Heredado | P1 | Grupos, repechaje, cuadro, podio | Completado |
| F06 | Universidades | 40 | Heredado | P1 + P2 | Dos repechajes, rondas posteriores y podio | Completado |
| F07 | Colegios | 40 | Progresivo | P1 | Repechaje único y cuadro posterior | Completado sin duplicados |
| F08 | Colegios | 40 | Progresivo | P1 + P2 | Ronda normal entre repechajes; candidatos disjuntos | Completado sin reutilización |
| F09 | Colegios | 17 y 33 | Progresivo | Según perfil | Cantidades excedentes, rondas balanceadas y podio | Ambos completados |
| F10 | Colegios | 8 | Interfaz real sobre SQLite aislada | 0 | Grupos, guardado, recarga, semifinal, corrección, final, tercer lugar y podio | Estado `Completado` |

## Casos humanos y de persistencia

| Caso | Resultado |
| --- | --- |
| Guardar el mismo resultado de grupo dos veces | Idempotente; no duplica historial |
| Guardar el mismo ganador dos veces | Idempotente; no crea avances repetidos |
| Doble clic en guardado general | Una confirmación y un resultado persistido |
| Formulario vacío o incompleto | JSON estructurado con HTTP 400 |
| ID de grupo o batalla de otra competencia | Rechazado con HTTP 400 |
| Corrección sin confirmar | HTTP 409; no cambia el resultado |
| Cancelar corrección | Resultado previo permanece intacto |
| Confirmar corrección | Recalcula dependencias y elimina únicamente resultados incompatibles |
| Dos pestañas con selección obsoleta | La segunda recibe HTTP 409 |
| Petición sin CSRF | HTTP 403 |
| Recarga después de guardar | Selecciones y clases visuales persisten |
| Corrección de semifinal con podio guardado | Podio y resultados dependientes se invalidan |
| Corrección profunda de grupo | Conserva semifinal paralela no afectada y reconstruye la rama afectada |
| P2 inmediatamente después de P1 | No se ofrece y el servicio lo rechaza por falta de elegibles nuevos |
| Cierre de final antes de tercer lugar | El torneo no se marca completado |
| Podio final | Campeón, subcampeón y tercero únicos |

## Validación visual

En una base SQLite temporal se operó la interfaz con 8 equipos por categoría:

- Grupos A y B: selección, confirmación, guardado y recarga.
- Clases visuales: `is-winner`/`entry-card--winner`, `is-loser`/`entry-card--loser` y pendientes coherentes con la selección.
- Creación de semifinal desde la recomendación.
- Corrección de un ganador: cancelar conservó el dato; confirmar sustituyó al semifinalista.
- Creación conjunta de final y tercer lugar.
- Guardado del bronce, final y podio.
- Vista de Colegios: `Completado`.
- Vista de Universidades: continuó en `Borrador` con 0/2 seleccionados por grupo.
- Modal de participante: quedó informativo e histórico, sin controles de movimiento arbitrario.
- Consola del navegador: 0 errores y 0 advertencias.
