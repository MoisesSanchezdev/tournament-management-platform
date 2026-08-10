# Matriz procedimientos-capturas

| Procedimiento | Perfil | Capítulo | Capturas | Reutilización | Advertencia | Estado |
| --- | --- | --- | --- | --- | --- | --- |
| P-01 | Consultar información pública del torneo | Visitante | 03 | MU-001 | MU-001 puede reutilizarse como entrada general. | No aplica | Incluido |
| P-02 | Consultar reglas oficiales y PDF | Visitante | 03 | MU-002 | Referencia cruzada desde consulta pública. | Verificar vigencia de reglas. | Incluido |
| P-03 | Consultar patrocinadores | Visitante | 03 | MU-003 | Uso contextual. | Marcas solo en entorno demo. | Incluido |
| P-04 | Elegir categoría de registro | Participante | 04 | MU-004 | Entrada para escolar y universitario. | Seleccionar categoría correcta. | Incluido |
| P-05 | Registrar robot escolar | Participante | 04 | MU-005, MU-006, MU-008 | MU-006 cubre validación. | Datos personales en operación real. | Incluido |
| P-06 | Registrar robot universitario | Participante | 04 | MU-007, MU-008 | MU-008 se comparte con registro escolar. | Semestre máximo. | Incluido |
| P-07 | Corregir errores de formulario antes de enviar | Participante | 04 | MU-006 | Se referencia desde ambos registros. | No insistir con datos duplicados. | Incluido |
| P-08 | Confirmar asistencia por token | Participante | 04 | MU-009, MU-010, MU-011 | MU-011 cubre enlace inválido. | No compartir tokens. | Incluido |
| P-09 | Iniciar sesión en panel interno | Organizador | 02 | MU-012 | Se referencia desde módulos internos. | No capturar credenciales. | Incluido |
| P-10 | Generar o asegurar tablero de competencia | Operador torneo | 05, 06 | MU-013, MU-014, MU-015 | MU-013 contextual. | No regenerar sin revisar progreso. | Agrupado |
| P-11 | Aplicar modo sugerido o formato manual | Operador torneo | 06 | MU-015, MU-016 | MU-015 contextual. | Impacta estructura inicial. | Incluido |
| P-12 | Ajustar distribución manual de grupos | Operador torneo | 06 | MU-017 | Uso puntual. | Mover equipos con cuidado. | Incluido |
| P-13 | Guardar clasificados de grupos | Operador torneo | 07 | MU-018, MU-019 | MU-019 se resuelve editorialmente. | Confirmación sensible. | Incluido |
| P-14 | Guardar ganador de batalla | Operador torneo | 08 | MU-026 | Base para eliminatorias. | Afecta fases posteriores. | Incluido |
| P-15 | Guardar clasificados múltiples de batalla | Operador torneo | 08 | MU-027 | Base para campales. | Respetar número requerido. | Incluido |
| P-16 | Usar guardado general de resultados | Operador torneo | 07 | MU-020 | Referencia desde grupos y batallas. | Guardar solo cambios revisados. | Incluido |
| P-17 | Crear fase recomendada | Operador torneo | 08 | MU-021, MU-022 | MU-021 muestra modal general. | No avanzar con resultados incompletos. | Incluido |
| P-18 | Crear repechaje | Operador torneo | 08 | MU-023 | Secuencia del mismo modal. | Evitar duplicar fases. | Incluido |
| P-19 | Generar y confirmar fase manual | Operador torneo | 08 | MU-024, MU-025 | Procedimiento avanzado. | Revisar propuesta antes de aceptar. | Incluido |
| P-20 | Corregir resultado con confirmación manual | Operador torneo | 10 | MU-028 | Elemento editorial reusable. | manual_override es sensible. | Incluido |
| P-21 | Editar estado de participante en modal | Operador torneo | 10 | MU-029, MU-030 | MU-029 sirve como detalle. | Evitar destinos incompatibles. | Incluido |
| P-22 | Guardar podio final | Operador torneo | 09 | MU-031 | Cierre de competencia. | No duplicar posiciones. | Incluido |
| P-23 | Gestionar plantillas de comunicación | Operador comunicaciones | 11 | MU-033, MU-034, MU-035 | Secuencia completa. | No subir archivos sensibles. | Incluido |
| P-24 | Gestionar destinatarios | Operador comunicaciones | 11 | MU-036, MU-037 | MU-036 contextual. | Correos reales en operación real. | Incluido |
| P-25 | Procesar invitaciones en simulación o prueba | Operador comunicaciones | 11 | MU-032, MU-036, MU-039 | MU-032 entrada al módulo. | Evitar envío real accidental. | Incluido |
| P-26 | Enviar solicitudes de asistencia | Operador comunicaciones | 11 | MU-038 | Referencia desde asistencia. | Confirmar modo dry-run/test. | Incluido |
| P-27 | Consultar historial de comunicaciones | Operador comunicaciones | 11 | MU-039 | Tabla de auditoría. | Privacidad de correos. | Incluido |
| P-28 | Revisar y corregir datos desde Django Admin | Superusuario | 12 | MU-040, MU-041, MU-042 | Anexo de administración. | Evitar cambios masivos no revisados. | Incluido |

Total: 28 procedimientos incluidos o agrupados justificadamente. No hay procedimientos obligatorios sin capítulo.
