# Riesgos operativos

| ID | Riesgo | Evidencia | Impacto | Mitigacion para manual |
| --- | --- | --- | --- | --- |
| RO-01 | Correcciones afectan fases posteriores | `ManualCorrectionRequired`, `manual_override` y confirmacion AJAX | Alto | Documentar advertencia y capturar confirmacion |
| RO-02 | Estado visual no persistido | `control.js` marca tarjetas antes de guardar | Medio | Explicar diferencia entre seleccionar y guardar |
| RO-03 | Recarga o refresco parcial desactualizado | `refreshControlContent` depende de `data-control-main` | Medio | Indicar que se revise mensaje de exito |
| RO-04 | Acciones Admin directas | Modelos registrados en Admin y acciones masivas | Alto | Separar Admin como capitulo avanzado |
| RO-05 | Formularios modificados sin guardar | Guardado individual/masivo con formularios dirty | Alto | Capturar boton Guardar todos y mensajes |
| RO-06 | Errores de red AJAX | `saveResultForm` espera JSON | Medio | Incluir procedimiento de verificacion posterior |
| RO-07 | Datos incompletos | Validaciones de formularios y servicios | Medio | Mostrar errores comunes con datos ficticios |
| RO-08 | Uso incorrecto de `manual_override` | Reintento tras confirmacion | Alto | Tratarlo como contingencia, no flujo normal |
| RO-09 | Acciones destructivas | `reset_competition`, `reset_tournament_demo.py` | Alto | No capturar ni recomendar en datos reales |
| RO-10 | Exposicion de PII | Registros, participantes, correos, documentos | Alto | Usar datos demo y enmascarar |
| RO-11 | Diferencia entre interfaz y persistencia | Selecciones locales antes de POST | Medio | Reforzar confirmacion de guardado |
| RO-12 | Envio real de correos | Modos TEST/OFFICIAL y SMTP | Alto | Documentar dry-run como opcion predeterminada |
| RO-13 | Plantillas con marcadores faltantes | `CommunicationTemplateForm` valida DOCX | Medio | Capturar error con plantilla demo |
| RO-14 | Excel de destinatarios mal formado | `load_recipients_from_xlsx` exige columnas | Medio | Incluir formato esperado |
| RO-15 | Token de asistencia filtrado | URL con UUID | Alto | Nunca mostrar tokens reales |

## Riesgo de datos demo

El comando `reset_tournament_demo.py` es destructivo: ejecuta `.delete()` sobre modelos de fases, batallas, grupos, competencias, equipos, instituciones, registros, reglas y ediciones. No debe usarse como preparacion de capturas salvo en una base temporal confirmada y aislada.

Estado: **PENDIENTE DE PREPARAR DATOS DE DEMOSTRACION**.
