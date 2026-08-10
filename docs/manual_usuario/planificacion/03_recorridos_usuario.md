# Recorridos de usuario

## Recorridos identificados

| ID | Recorrido | Perfil | Precondiciones | Inicio | Pasos resumidos | Resultado esperado | Riesgos | Capturas |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| R-01 | Consulta del sitio publico | Visitante | Sitio disponible | `/` | Abrir inicio, revisar edicion, conteos, reglas y patrocinadores | Usuario entiende evento y opciones | Informacion vacia si no hay edicion activa | MU-001 |
| R-02 | Consulta de reglas y patrocinadores | Visitante | Reglas o catalogo | `/reglas/` | Abrir reglas, PDF, patrocinadores | Consulta informativa completa | PDF externo/desactualizado, enlaces no listos | MU-002, MU-003 |
| R-03 | Registro escolar | Participante | Edicion activa | `/registro/` | Elegir colegios, llenar datos, enviar | Registro submitted y pagina de exito | Duplicados, correo fallido, datos personales | MU-004, MU-005 |
| R-04 | Registro universitario | Participante | Edicion activa | `/registro/` | Elegir universidades, completar semestre y datos, enviar | Registro submitted y exito | Semestre > 4, duplicados, correo fallido | MU-006, MU-007 |
| R-05 | Confirmacion mediante token | Participante | Token valido | Enlace recibido | Abrir token, revisar datos, confirmar asistencia | Registro aprobado, equipo sincronizado, posible competencia inicializada | Exponer token, confirmar registro equivocado | MU-008, MU-009 |
| R-06 | Token invalido | Participante | Token inexistente | Enlace token | Abrir enlace | Pantalla enlace no valido | Confusion del usuario | MU-010 |
| R-07 | Gestion de instituciones y participantes | Superusuario | Login Admin | `/admin/` | Abrir registros, revisar participantes, editar si procede | Datos corregidos o revisados | Saltar validaciones de interfaz | MU-011 |
| R-08 | Formacion y edicion de equipos | Superusuario/organizador | Registros confirmados | Admin o confirmacion | Sincronizar confirmados, revisar equipos y miembros | Equipos listos para competencia | Borrar miembros en resync, datos reales | MU-012 |
| R-09 | Configuracion/inicializacion de competencia | Operador torneo | Equipos aprobados | `/torneo/control/` | Crear tablero base por division | `DivisionCompetition` con grupos/estados | Inicializar con datos incompletos | MU-013 |
| R-10 | Control de fase de grupos | Operador torneo | Competencia con grupos | Fase groups | Seleccionar clasificados por grupo, guardar individual o masivo | Grupos cerrados y estados sincronizados | Cantidad incorrecta, seleccion visual no guardada | MU-014, MU-015 |
| R-11 | Seleccion de clasificados | Operador torneo | Grupos con participantes | Fase groups | Marcar checkboxes, confirmar guardado | Clasificados persistidos | Cambiar clasificados luego de avanzar | MU-015 |
| R-12 | Registro de ganador de batalla | Operador torneo | Batalla creada | Fase posterior | Seleccionar ganador radio, guardar | Batalla finalizada con ganador | Ganador incorrecto afecta cruces | MU-016 |
| R-13 | Registro de clasificados de batalla | Operador torneo | Batalla multi-clasificador | Fase posterior | Seleccionar varios clasificados, respetar contador, guardar | Clasificados persistidos | Numero distinto al requerido | MU-017 |
| R-14 | Repechaje | Operador torneo | Etapa cerrada y candidatos | Modal decision | Abrir modal, elegir repechaje, confirmar | Fase de repechaje creada o reutilizada | Duplicar fase o abrir antes de cerrar | MU-018, MU-019 |
| R-15 | Fases progresivas | Operador torneo | Etapa actual cerrada | Modal decision | Usar recomendacion, confirmar creacion | Siguiente fase materializada | Crear fase con resultados incompletos | MU-020 |
| R-16 | Fases manuales | Operador torneo | Participantes elegibles | Modal decision | Abrir configuracion manual, generar propuesta, revisar, confirmar | Fase personalizada creada | Propuesta obsoleta, grupos vacios, duplicados | MU-021, MU-022 |
| R-17 | Correccion con `manual_override` | Operador torneo | Progreso posterior existente | Guardado AJAX | Cambiar resultado, recibir confirmacion, aceptar o cancelar | Correccion aplicada solo si se confirma | Incoherencia en fases posteriores | MU-023 |
| R-18 | Actualizacion mediante modal | Operador torneo | Estado de participante | Click participante | Abrir modal, mover fase/grupo/batalla, estado, nota, guardar | Estado e historial actualizados | Mover a destino incompatible | MU-024 |
| R-19 | Uso del guardado general | Operador torneo | Varias selecciones modificadas | Fase actual | Modificar resultados visibles, presionar guardar todos | Guardado secuencial con mensajes | Guardar cambios no revisados | MU-025 |
| R-20 | Gestion de plantillas de comunicacion | Operador comunicaciones | Usuario staff | `/comunicaciones/plantillas/` | Crear plantilla DOCX, definir marcadores, previsualizar | Plantilla activa valida | Marcadores faltantes, archivo sensible | MU-026, MU-027 |
| R-21 | Gestion de destinatarios | Operador comunicaciones | Usuario staff | `/comunicaciones/invitaciones/` | Registrar destinatario manual o preparar Excel | Destinatarios disponibles | Correos personales, JSON extra mal formado | MU-028 |
| R-22 | Creacion y seguimiento de invitaciones | Operador comunicaciones | Plantilla activa | Invitaciones | Elegir tipo, plantilla, modo dry-run/test/oficial, procesar | Lote y logs creados | Envio real accidental | MU-029, MU-030 |
| R-23 | Consulta de historial | Operador comunicaciones | Logs existentes | `/comunicaciones/historial/` | Revisar lotes, estados y errores | Trazabilidad de comunicacion | Exponer correos reales en capturas | MU-031 |
| R-24 | Operaciones relevantes en Django Admin | Superusuario | Admin demo | `/admin/` | Revisar modelos, filtros, acciones de asistencia/sync | Mantenimiento directo | Acciones masivas o CRUD riesgoso | MU-032, MU-033 |
| R-25 | Cierre y consulta de podio | Operador torneo | Final disponible | Fase final | Seleccionar campeon, segundo y tercero si aplica, confirmar | Competencia completada con podio | Posiciones duplicadas o final incompleta | MU-034, MU-035 |

Total de recorridos identificados: **25**.

## Mensajes posibles por flujo

- Registro: inscripcion recibida y correo enviado; inscripcion guardada pero correo no enviado; errores de duplicidad; no existe edicion activa.
- Asistencia: asistencia confirmada; asistencia ya confirmada; no fue posible confirmar; enlace no valido.
- Torneo: tablero asegurado; formato manual aplicado; seleccion guardada; correccion aplicada; completa resultados antes de avanzar; reinicio destructivo requiere confirmacion.
- AJAX: respuesta `ok`, `requires_confirmation`, error de validacion o respuesta inesperada.
- Comunicaciones: plantilla guardada y validada; falta plantilla activa; lote procesado como simulacion/prueba/envio real; SMTP bloqueado; no hay destinatarios.
