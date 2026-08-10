# Capturas no automatizadas

Solo se listan capturas cuyo estado visual objetivo incluye dialogos nativos no renderizados por el screenshot PNG headless.

| ID | Razon tecnica | Procedimiento | Estado requerido | Pasos exactos | Usuario demo | URL | Datos visibles | Area a capturar | Resolucion | Riesgo | Alternativa documental |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| MU-019 | El dialogo `window.confirm` de guardado de grupo no se renderiza en el PNG headless; se genero la pantalla previa con el boton y seleccion visible. | Fase grupos | Seleccion hecha en un grupo | Entrar a grupos, cambiar un clasificado y pulsar Guardar este grupo. | staff demo | /torneo/control/divisiones/<id>/fases/groups/ | Robots ficticios y boton de guardado | Dialogo nativo del navegador o estado previo | 1440x900 | Medio | Usar captura previa y recrear editorialmente solo el dialogo con texto exacto. |
| MU-028 | La confirmacion de `manual_override` depende de un segundo `window.confirm`; CDP puede aceptar el evento, pero el dialogo nativo no aparece dentro de la captura headless. | Correcciones | Resultado ya guardado con fase posterior iniciada | Entrar a semifinal, cambiar el ganador guardado y confirmar la correccion manual. | staff demo | /torneo/control/divisiones/<id>/fases/semifinal/ | Robots ficticios y cambio de ganador | Dialogo de confirmacion manual_override | 1440x900 | Alto | Usar captura previa y documentar el texto exacto. |

Textos nativos documentados desde el codigo:

- Guardado de resultados: `¿Seguro que deseas guardar estas selecciones? Podrás editarlas después, pero verifica bien antes de continuar.`
- Confirmacion de correccion: `Este cambio puede afectar fases posteriores ya iniciadas. ¿Deseas aplicar la corrección manual?`
