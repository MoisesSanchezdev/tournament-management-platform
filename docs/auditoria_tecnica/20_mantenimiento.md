# 20. Mantenimiento

## Areas de mantenimiento

| Area | Archivo(s) |
| --- | --- |
| Configuracion | `config/settings.py`, `.env.example` |
| Dominio torneo | `apps/tournament/models.py`, `services.py`, `formats.py`, `recommendations.py`, `planner.py` |
| Registro | `apps/participants/models.py`, `forms.py`, `services.py`, `views.py` |
| Comunicaciones | `apps/invitations/models.py`, `forms.py`, `services.py`, `views.py`, comandos |
| Frontend | `static/css/app.css`, `static/js/app.js`, `static/js/control.js`, templates |
| Datos demo | `apps/tournament/management/commands/reset_tournament_demo.py` |

## Comandos de gestion

| Comando | Archivo | Uso |
| --- | --- | --- |
| `bootstrap_tournament` | `apps/tournament/management/commands/bootstrap_tournament.py` | Crea edicion inicial y reglas base |
| `reset_tournament_demo` | `apps/tournament/management/commands/reset_tournament_demo.py` | Limpia datos operativos y crea simulacion |
| `send_invitations` | `apps/invitations/management/commands/send_invitations.py` | Procesa invitaciones desde XLSX |
| `send_attendance_requests` | `apps/invitations/management/commands/send_attendance_requests.py` | Envia/simula solicitudes de asistencia |

## Precauciones operativas

| Accion | Precaucion |
| --- | --- |
| `reset_tournament_demo` | Es destructivo: elimina datos de torneo, registros, equipos e instituciones |
| Envio oficial | Requiere `--yes` o confirmacion UI |
| Prueba controlada | Usar `test_recipient` para evitar envio a destinatarios reales |
| Accion admin `send_attendance_requests` | Puede enviar correos de confirmacion desde Django Admin; depende de configuracion de correo |
| Accion admin `sync_confirmed_to_teams` | Crea/actualiza equipos desde registros confirmados; validar seleccion antes de ejecutar |
| Cambios en `services.py` | Requieren pruebas de regresion por alta concentracion de reglas |
| Cambios en `control.js` | Verificar manualmente flujos AJAX y modales |

## Checklist recomendado antes de evento real

1. Validar `.env` sin placeholders.
2. Ejecutar `manage.py check --deploy`.
3. Confirmar PostgreSQL y backups.
4. Probar SMTP con modo `test`.
5. Probar LibreOffice con una plantilla DOCX.
6. Crear edicion activa real.
7. Validar formularios de registro.
8. Confirmar que solo staff autorizado acceda al panel.
9. Hacer simulacion completa de grupos, eliminatorias, repechaje y podio.

## Deuda de mantenimiento detectada

| Deuda | Impacto |
| --- | --- |
| `apps/tournament/services.py` muy extenso | Dificulta cambios localizados |
| Pruebas limitadas | Mayor esfuerzo manual para validar |
| Documentacion de `configuration` JSON incompleta | Riesgo al extender fases |
| Frontend interno acoplado a HTML | Cambios de template pueden romper JS |
| Acciones operativas tambien disponibles en Django Admin | Requieren procedimientos claros para evitar envios o sincronizaciones accidentales |

## No confirmado

| Punto | Estado |
| --- | --- |
| Responsable de mantenimiento | NO CONFIRMADO |
| Politica de versionado | NO CONFIRMADO |
| Calendario de backups | NO CONFIRMADO |
| Monitoreo de errores | NO CONFIRMADO |

## Mejora realizada en Fase 2

Se incorporaron las acciones administrativas de `participants/admin.py` al plan de mantenimiento, porque forman parte del flujo operativo real de asistencia y sincronizacion a equipos.
