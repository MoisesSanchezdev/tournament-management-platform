# Plan de capturas

## Inventario profesional

| ID | Archivo propuesto | Tipo | Pantalla | Estado previo | Accion visible | Area a resaltar | Datos de demostracion | Riesgo datos sensibles | Capitulo |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| MU-001 | `MU-001-inicio-publico.png` | completa | PU-001 | Edicion demo activa | Entrada publica | Hero, conteos, botones | Datos ficticios | Bajo | Primeros pasos |
| MU-002 | `MU-002-reglas-publicas.png` | completa | PU-002 | Reglas demo publicadas | Consultar reglas | Secciones y PDF | Reglas demo | Bajo | Consulta publica |
| MU-003 | `MU-003-patrocinadores.png` | completa | PU-003 | Catalogo disponible | Consultar aliados | Tarjetas y enlaces | Logos autorizados | Medio por marcas | Consulta publica |
| MU-004 | `MU-004-seleccion-registro.png` | completa | REG-001 | Sin login | Elegir categoria | Tarjetas colegio/universidad | Ninguno | Bajo | Registro |
| MU-005 | `MU-005-registro-escolar.png` | recorte | REG-002 | Edicion demo | Llenar formulario | Datos robot e integrantes | Nombres ficticios | Alto | Registro escolar |
| MU-006 | `MU-006-registro-escolar-error.png` | mensaje | REG-002 | Duplicado ficticio | Error de validacion | Mensajes del formulario | Datos ficticios | Medio | Registro escolar |
| MU-007 | `MU-007-registro-universitario.png` | recorte | REG-003 | Edicion demo | Llenar semestre | Campo semestre | Datos ficticios | Alto | Registro universitario |
| MU-008 | `MU-008-registro-exito.png` | completa | REG-004 | Registro enviado | Confirmacion | Botones posteriores | Sin PII | Bajo | Registro |
| MU-009 | `MU-009-confirmacion-asistencia.png` | completa | REG-005 | Token demo valido | Confirmar asistencia | Boton confirmar | Robot ficticio | Alto por token | Asistencia |
| MU-010 | `MU-010-asistencia-confirmada.png` | mensaje | REG-005 | Ya confirmada | Estado confirmado | Mensaje | Robot ficticio | Medio | Asistencia |
| MU-011 | `MU-011-token-invalido.png` | completa | REG-006 | Token ficticio | Enlace invalido | Mensaje 404 | Sin token real | Bajo | Asistencia |
| MU-012 | `MU-012-login-panel.png` | completa | INT-001 | Usuario demo | Login | Formulario acceso | Sin credenciales visibles | Medio | Acceso |
| MU-013 | `MU-013-panel-torneo.png` | completa | TOR-001 | Login staff | Resumen | Divisiones y conteos | Datos ficticios | Medio | Operacion |
| MU-014 | `MU-014-generar-competencia.png` | secuencia | TOR-001 | Equipos aprobados | Crear tablero base | Boton por division | Datos ficticios | Medio | Operacion |
| MU-015 | `MU-015-configuracion-division.png` | completa | TOR-002 | Competencia creada | Revisar formato | Estadisticas y recomendacion | Datos ficticios | Medio | Configuracion |
| MU-016 | `MU-016-formato-manual.png` | recorte | TOR-002 | Sin progreso | Aplicar formato manual | Campos grupos/clasificados | Datos ficticios | Medio | Configuracion |
| MU-017 | `MU-017-distribucion-grupos.png` | recorte | TOR-002 | Grupos creados | Mover equipo entre grupos | Selects de destino | Datos ficticios | Alto | Configuracion |
| MU-018 | `MU-018-clasificados-grupo.png` | completa | TOR-005 | Fase grupos | Seleccionar clasificados | Tarjetas y contador | Robots ficticios | Medio | Fase grupos |
| MU-019 | `MU-019-guardar-grupo.png` | mensaje | TOR-005 | Seleccion hecha | Guardar | Confirmacion/alert | Robots ficticios | Medio | Fase grupos |
| MU-020 | `MU-020-guardar-todos.png` | secuencia | TOR-005/TOR-006 | Varios cambios | Guardar todos | Boton global | Robots ficticios | Medio | Guardado |
| MU-021 | `MU-021-modal-siguiente-fase.png` | modal | TOR-003 | Etapa cerrada | Pasar a fase | Modal completo | Datos ficticios | Medio | Avance |
| MU-022 | `MU-022-crear-fase-recomendada.png` | secuencia | TOR-003 | Recomendacion lista | Confirmar | Vista previa | Datos ficticios | Medio | Avance |
| MU-023 | `MU-023-repechaje.png` | modal | TOR-003 | Candidatos | Confirmar repechaje | Opcion repechaje | Datos ficticios | Medio | Repechaje |
| MU-024 | `MU-024-asistente-manual.png` | modal | TOR-004 | Elegibles | Generar propuesta | Distribucion, resumen | Datos ficticios | Medio | Fase manual |
| MU-025 | `MU-025-propuesta-manual.png` | recorte | TOR-004 | Propuesta generada | Reasignar/confirmar | Tabla propuesta | Datos ficticios | Alto | Fase manual |
| MU-026 | `MU-026-batalla-ganador.png` | completa | TOR-006 | Batalla creada | Marcar ganador | Radios/tarjetas | Robots ficticios | Medio | Batallas |
| MU-027 | `MU-027-batalla-clasificados.png` | completa | TOR-006 | Batalla multi | Marcar clasificados | Checkboxes/contador | Robots ficticios | Medio | Batallas |
| MU-028 | `MU-028-confirmacion-correccion.png` | mensaje | TOR-006 | Fase posterior iniciada | Cambiar resultado | `manual_override` confirm | Robots ficticios | Alto | Correcciones |
| MU-029 | `MU-029-modal-participante.png` | modal | TOR-007 | Participante demo | Abrir detalle | Resumen e historial | Robots ficticios | Medio | Control manual |
| MU-030 | `MU-030-edicion-participante.png` | modal | TOR-007 | Modal abierto | Guardar cambios | Campos estado/fase/grupo | Datos ficticios | Alto | Control manual |
| MU-031 | `MU-031-podio-final.png` | completa | TOR-008 | Final lista | Seleccionar podio | Selects de posiciones | Robots ficticios | Medio | Cierre |
| MU-032 | `MU-032-dashboard-comunicaciones.png` | completa | COM-001 | Staff login | Revisar indicadores | Totales y estado correo | Datos ficticios | Medio | Comunicaciones |
| MU-033 | `MU-033-lista-plantillas.png` | completa | COM-002 | Plantillas demo | Listar plantillas | Tabla y botones | Nombres ficticios | Bajo | Plantillas |
| MU-034 | `MU-034-nueva-plantilla.png` | recorte | COM-003 | DOCX demo | Cargar plantilla | Campos y marcadores | Archivo demo | Medio | Plantillas |
| MU-035 | `MU-035-preview-plantilla.png` | completa | COM-004 | Plantilla cargada | Previsualizar | Marcadores detectados | Plantilla demo | Medio | Plantillas |
| MU-036 | `MU-036-invitaciones-lote.png` | completa | COM-005 | Plantilla activa | Procesar lote | Modo de envio y archivo | Excel demo | Alto por correos | Invitaciones |
| MU-037 | `MU-037-destinatario-manual.png` | recorte | COM-005 | Staff login | Guardar destinatario | Formulario manual | Correo ficticio | Alto | Destinatarios |
| MU-038 | `MU-038-confirmaciones-asistencia.png` | completa | COM-006 | Registros submitted | Simular o prueba | Botones por registro | Registros ficticios | Alto | Confirmaciones |
| MU-039 | `MU-039-historial-comunicaciones.png` | completa | COM-007 | Logs demo | Consultar historial | Estados de logs | Correos enmascarados | Alto | Historial |
| MU-040 | `MU-040-admin-modelos.png` | completa | ADM-002 | Admin demo | Ver modelos | Indice Admin | Sin PII visible | Medio | Administracion |
| MU-041 | `MU-041-admin-registros.png` | recorte | ADM-003 | Datos demo | Revisar registros | Filtros y acciones | Datos ficticios | Alto | Administracion |
| MU-042 | `MU-042-admin-torneo.png` | recorte | ADM-004 | Datos demo | Revisar competencias | Filtros | Datos ficticios | Medio | Administracion |

Total estimado: **42 capturas**.

## Reutilizacion

- MU-013 puede reutilizarse para introduccion del panel y ubicacion de divisiones.
- MU-018 y MU-020 pueden reutilizarse en los capitulos de grupos y guardado general.
- MU-021 puede reutilizarse para explicar avance recomendado, repechaje y fase manual si se agregan recortes internos.
- MU-029 puede reutilizarse para control manual e historial de participante.
- MU-032 puede reutilizarse como entrada de todo el modulo de comunicaciones.

## Condicion previa obligatoria

Antes de capturar nuevas imagenes: **PENDIENTE DE PREPARAR DATOS DE DEMOSTRACION** en una base temporal, sin nombres reales, correos personales, documentos, tokens reales ni credenciales.
