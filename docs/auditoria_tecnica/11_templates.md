# 11. Templates

## Bases

| Template | Uso |
| --- | --- |
| `apps/core/templates/core/base.html` | Layout publico |
| `apps/tournament/templates/tournament/control_base.html` | Layout interno para torneo y comunicaciones |

Ambos cargan `static/css/app.css` y control de tema. `core/base.html` carga `static/js/app.js`; `control_base.html` carga `static/js/control.js`.

## Templates publicos core

| Template | Contenido |
| --- | --- |
| `core/home.html` | Hero, estado de evento, reglas, imagenes, patrocinadores |
| `core/rules.html` | Reglas publicadas y PDF embebido |
| `core/sponsors.html` | Catalogo de patrocinadores |

## Templates participants

| Template | Contenido |
| --- | --- |
| `registration_choice.html` | Seleccion colegio/universidad |
| `registration_form.html` | Formulario generico de registro |
| `registration_success.html` | Confirmacion posterior a registro |
| `attendance_confirmation.html` | Confirmacion por token |
| `attendance_not_found.html` | Token no encontrado |

## Templates tournament

| Template | Contenido |
| --- | --- |
| `overview.html` | Vista publica de torneo |
| `internal_login.html` | Login interno |
| `control_dashboard.html` | Resumen de divisiones y generacion de competencia |
| `control_division.html` | Operacion por division completa |
| `control_stage.html` | Operacion por fase |
| `control_phase_detail.html` | Detalle de fase generica |
| `_manual_phase_assistant.html` | Asistente de fase manual y vista previa |

## Templates invitations

| Template | Contenido |
| --- | --- |
| `_nav.html` | Navegacion de comunicaciones |
| `dashboard.html` | Indicadores del modulo |
| `template_list.html` | Listado de plantillas |
| `template_form.html` | Carga de plantilla DOCX |
| `template_preview.html` | Marcadores detectados |
| `invitations.html` | Destinatarios y envio de invitaciones |
| `confirmations.html` | Solicitudes de asistencia |
| `history.html` | Lotes y logs |

## Uso de CSRF

Se confirmo uso de `{% csrf_token %}` en formularios POST de logout, registros, confirmacion de asistencia, panel de torneo, asistente manual y comunicaciones.

## Integracion con JavaScript

| Atributo | Uso |
| --- | --- |
| `data-control-main` | Contenido refrescable por AJAX |
| `data-participant-modal` | Modal de participante |
| `data-result-form` | Formularios de resultados |
| `data-save-all-results` | Guardado multiple |
| `data-phase-decision-modal` | Modal de decision de siguiente fase |
| `data-manual-phase-form` | Asistente de fase manual |
| `data-manual-assignment` | Reasignacion en propuesta manual |

## Observaciones

1. Los templates publicos e internos comparten hoja de estilos.
2. El panel interno esta fuertemente acoplado a `control.js` mediante `data-*`.
3. El template `_manual_phase_assistant.html` concentra una parte importante del flujo manual de torneo.
