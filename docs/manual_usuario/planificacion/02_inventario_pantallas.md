# Inventario de pantallas

## Pantallas publicas

| ID | Titulo visible | Ruta | Perfil | Proposito | Datos mostrados | Acciones | Estados/mensajes | Captura | Datos previos |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| PU-001 | Torneo Robot Explota Globos | `/` | Visitante | Entrada publica | Edicion activa, reglas destacadas, conteos, patrocinadores | Registrar robot, consultar reglamento, ver patrocinadores, cambiar tema | Sin edicion activa, mensajes Django | Si | Edicion activa deseable |
| PU-002 | Reglas del torneo | `/reglas/` | Visitante | Consultar reglas | Reglas publicadas, PDF oficial | Abrir PDF | Reglamento pendiente | Si | Reglas publicadas o estado vacio |
| PU-003 | Aliados del torneo | `/patrocinadores/` | Visitante | Consultar patrocinadores | Catalogo de patrocinadores y enlaces disponibles | Abrir enlaces externos | Enlaces no disponibles | Si | Ninguno |
| PU-004 | Fases del torneo | `/torneo/` | Visitante | Consulta publica de fases | Edicion activa, fases publicas | Navegar | Fases pendientes | Si | Edicion/fases publicas |

## Registro y asistencia

| ID | Titulo visible | Ruta | Perfil | Proposito | Formularios/botones | Estados/mensajes | Captura | Datos previos |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| REG-001 | Inscribe tu robot en la categoria correcta | `/registro/` | Participante | Elegir categoria | Ir a colegios, ir a universidades, consultar reglas | No aplica | Si | Ninguno |
| REG-002 | Registro de colegios | `/registro/colegios/` | Participante | Registrar robot escolar | Formulario de institucion, responsable, robot, contacto, lider e integrantes; Enviar inscripcion | Errores de edicion activa, duplicados, campos incompletos, correo enviado/no enviado | Si | Edicion activa |
| REG-003 | Registro de universidades | `/registro/universidades/` | Participante | Registrar robot universitario | Igual a escolar mas semestre; Enviar inscripcion | Semestre mayor a 4, duplicados, correo enviado/no enviado | Si | Edicion activa |
| REG-004 | Inscripcion registrada | `/registro/exito/<registration_type>/` | Participante | Confirmar recepcion del registro | Registrar otro equipo, volver al inicio | Mensaje de exito previo | Si | Registro enviado |
| REG-005 | Confirmar asistencia | `/registro/confirmar-asistencia/<token>/` | Participante | Confirmar asistencia con token valido | Confirmar asistencia | Asistencia ya confirmada, exito, error de servicio | Si | Token demo no sensible |
| REG-006 | Enlace no valido | `/registro/confirmar-asistencia/<token>/` | Participante | Informar token inexistente | Sin accion principal | Estado 404 visual | Si | Token ficticio |

## Panel interno de torneo

| ID | Titulo visible | Ruta | Perfil | Proposito | Formularios/botones | Acciones asincronas | Captura | Datos previos |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| INT-001 | Panel de organizacion | `/torneo/control/login/` | Organizador | Autenticacion | Usuario, contrasena, Ingresar al panel | No | Si | Usuario demo |
| TOR-001 | Panel de organizacion | `/torneo/control/` | Operador torneo | Resumen e inicializacion por division | Abrir division, crear tablero base | No | Si | Edicion activa y equipos aprobados |
| TOR-002 | Colegios/Universidades | `/torneo/control/divisiones/<competition_id>/` | Operador torneo | Resumen, configuracion y avance por division | Volver a mezclar grupos, usar modo sugerido, aplicar formato manual, guardar distribucion manual, pasar a siguiente fase | Modal decision de fase | Si | Competencia creada |
| TOR-003 | Pasar a la siguiente fase | Modal en division/etapa | Operador torneo | Decidir avance recomendado, repechaje o manual | Usar recomendacion, configurar manualmente, cancelar, confirmar repechaje, crear fase | Visibilidad JS | Si | Fase cerrada |
| TOR-004 | Preparar fase personalizada | Include/modal | Operador torneo | Generar propuesta manual | Operacion normal/repechaje, distribucion, grupos personalizados, clasifican, nombre; generar, regenerar, confirmar, cancelar | Calculo local JS | Si | Participantes elegibles |
| TOR-005 | Division - Grupos | `/torneo/control/divisiones/<id>/fases/groups/` | Operador torneo | Seleccionar clasificados de grupos | Checkboxes, guardar por grupo, guardar todos | POST AJAX con `save_group_qualifiers` | Si | Grupos creados |
| TOR-006 | Division - etapa posterior | `/torneo/control/divisiones/<id>/fases/<stage_key>/` | Operador torneo | Registrar batalla o clasificados multiples | Radios ganador o checkboxes; guardar batalla/guardar todos | POST AJAX con `save_battle_winner` o `save_battle_qualifiers` | Si | Fase materializada |
| TOR-007 | Participante | Modal AJAX | Operador torneo | Ver y editar estado de participante | Mover a fase/grupo/batalla, estado manual, nota, guardar cambios | GET/POST JSON | Si | Estado de equipo |
| TOR-008 | Podio final | Seccion en fase `final` | Operador torneo | Cerrar competencia | Select campeon, segundo, tercer lugar, guardar podio | No | Si | Final disponible |
| TOR-009 | Detalle de fase | `/torneo/control/fases/<phase_id>/` | Operador torneo | Consultar `TournamentPhase` generica | Sin accion critica visible | No | Opcional | Fase generica |

## Comunicaciones

| ID | Titulo visible | Ruta | Perfil | Proposito | Formularios/botones | Estados/mensajes | Captura | Datos previos |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| COM-001 | Comunicaciones | `/comunicaciones/` | Operador comunicaciones | Ver indicadores | Ver historial, nav interna | Configurado/bloqueado, totales | Si | Usuario staff |
| COM-002 | Plantillas | `/comunicaciones/plantillas/` | Operador comunicaciones | Listar plantillas | Nueva plantilla, previsualizar | Estado activo por tipo | Si | Plantillas demo |
| COM-003 | Nueva plantilla | `/comunicaciones/plantillas/nueva/` | Operador comunicaciones | Cargar plantilla DOCX | Nombre, tipo, archivo, marcadores, descripcion, activa, Guardar plantilla | Errores DOCX/tamano/marcadores | Si | DOCX demo |
| COM-004 | Nombre de plantilla | `/comunicaciones/plantillas/<id>/previsualizar/` | Operador comunicaciones | Revisar marcadores detectados | Abrir archivo | Error al leer plantilla | Si | Plantilla demo |
| COM-005 | Invitaciones | `/comunicaciones/invitaciones/` | Operador comunicaciones | Procesar lotes y registrar destinatarios | Tipo, plantilla, Excel, modo, correo prueba, confirmar envio real; guardar destinatario | Script filtra plantillas; mensajes de lote | Si | Plantilla y destinatarios demo |
| COM-006 | Confirmaciones | `/comunicaciones/confirmaciones/` | Operador comunicaciones | Solicitar asistencia | Simular, enviar prueba, enviar, reenviar | Bloqueos SMTP, confirmacion real | Si | Registros submitted demo |
| COM-007 | Historial | `/comunicaciones/historial/` | Operador comunicaciones | Auditar lotes y logs | Consulta | Estados simulado, prueba, enviado, fallido, omitido | Si | Logs demo anonimizados |

## Django Admin

| ID | Superficie | Ruta | Perfil | Proposito | Acciones | Captura | Datos previos |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ADM-001 | Login Admin | `/admin/login/` | Superusuario | Acceso admin | Login | Si | Superusuario demo |
| ADM-002 | Indice Admin | `/admin/` | Superusuario | Acceso a modelos | Abrir modelos | Si | Usuario admin |
| ADM-003 | Participantes Admin | `/admin/participants/.../` | Superusuario | Registros, instituciones, equipos | Acciones enviar confirmacion y sincronizar confirmados | Si | Datos demo anonimizados |
| ADM-004 | Torneo Admin | `/admin/tournament/.../` | Superusuario | Ediciones, reglas, competencias, grupos, batallas, estados, historial | CRUD directo | Si | Datos demo |
| ADM-005 | Comunicaciones Admin | `/admin/invitations/.../` | Superusuario | Plantillas, destinatarios, lotes y logs | CRUD e inspeccion | Si | Datos demo |

Total de pantallas/superficies inventariadas: **30**.
