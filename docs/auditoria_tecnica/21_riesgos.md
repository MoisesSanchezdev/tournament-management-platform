# 21. Riesgos

## Riesgos tecnicos

| ID | Riesgo | Evidencia | Severidad |
| --- | --- | --- | --- |
| R-01 | Alta concentracion de logica de torneo | `apps/tournament/services.py` contiene inicializacion, sincronizacion, fases, manual override y contexto | Alta |
| R-02 | Cobertura de pruebas insuficiente | Solo hay pruebas en `tournament` e `invitations` | Alta |
| R-03 | Comando demo destructivo | `reset_tournament_demo.py` elimina multiples modelos | Alta |
| R-04 | Dependencia de LibreOffice | `convert_docx_to_pdf` depende de binario externo | Media |
| R-05 | JSON dinamico en configuracion | `DivisionCompetition.configuration` almacena perfiles, propuestas y podio | Media |
| R-06 | Acoplamiento JS-template | `control.js` depende de muchos `data-*` | Media |
| R-07 | Falta de roles granulares | Acceso staff/superuser para panel | Media |
| R-08 | Datos personales en logs/previews | `CommunicationLog.rendered_preview` guarda contexto renderizado | Media |
| R-09 | Recursos externos en home | Imagenes remotas definidas en `core.views` | Baja |
| R-10 | Despliegue no documentado al detalle | No hay evidencia de hosting/CI/CD | Media |
| R-11 | Acciones operativas expuestas en Django Admin | `send_attendance_requests` y `sync_confirmed_to_teams` operan sobre registros seleccionados | Media |

## Riesgos funcionales

| Riesgo | Impacto |
| --- | --- |
| Reglas de torneo cambian durante el evento | Requiere validar manual overrides y flujo progresivo |
| Error en clasificados por grupo | Puede arrastrar estados y batallas posteriores |
| Repechaje abierto en momento incorrecto | Puede crear estados inconsistentes si no se respeta cierre de fase |
| Fallo SMTP | Participantes no reciben confirmaciones |
| Fallo PDF | Invitaciones no se adjuntan |

## Controles existentes

| Control | Riesgo mitigado |
| --- | --- |
| `ManualCorrectionRequired` | Cambios sobre fases posteriores |
| Firmas SHA-256 en propuesta manual | Cambios de participantes/propuesta antes de confirmar |
| `stage_is_closed` | Avance de fase sin resultados completos |
| Dry-run por defecto | Envio accidental de correos |
| Validacion SMTP | Envios reales sin configuracion |
| Restricciones DB | Duplicados de grupos, batallas, estados y registros |
| `manage.py check` sin issues | Validacion basica de configuracion Django |

## Recomendaciones priorizadas

1. Crear pruebas integrales del flujo de competencia.
2. Dividir `tournament.services` por subdominio: inicializacion, resultados, recomendaciones, manual phases, sync.
3. Bloquear o aislar `reset_tournament_demo` fuera de produccion.
4. Documentar schema de `DivisionCompetition.configuration`.
5. Agregar pruebas de permisos y vistas internas.
6. Validar despliegue con `check --deploy`, SMTP y LibreOffice.
7. Revisar privacidad de `CommunicationLog.rendered_preview`.
8. Documentar procedimiento de uso para acciones operativas disponibles desde Django Admin.

## Mejora realizada en Fase 2

Se agrego el riesgo R-11 asociado a acciones administrativas que pueden enviar solicitudes de asistencia o sincronizar equipos desde Django Admin.
