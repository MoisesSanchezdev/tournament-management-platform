# Matriz de trazabilidad funcional

| Procedimiento | URL | View | Template | JavaScript | Servicio | Perfil | Capturas | Capitulo futuro |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P-01 Consulta publica | `/` | `home` | `core/home.html` | `app.js` | No aplica | Visitante | MU-001 | Primeros pasos |
| P-02 Reglas | `/reglas/` | `rules_page` | `core/rules.html` | `app.js` | No aplica | Visitante | MU-002 | Consulta publica |
| P-03 Patrocinadores | `/patrocinadores/` | `sponsors_page` | `core/sponsors.html` | `app.js` | `sponsor_catalog` | Visitante | MU-003 | Consulta publica |
| P-04 Elegir registro | `/registro/` | `registration_choice` | `participants/registration_choice.html` | `app.js` | No aplica | Participante | MU-004 | Registro |
| P-05 Registro escolar | `/registro/colegios/` | `school_register` | `participants/registration_form.html` | `app.js` | `send_registration_received_email` | Participante | MU-005, MU-006 | Registro escolar |
| P-06 Registro universitario | `/registro/universidades/` | `university_register` | `participants/registration_form.html` | `app.js` | `send_registration_received_email` | Participante | MU-007 | Registro universitario |
| P-08 Confirmar asistencia | `/registro/confirmar-asistencia/<token>/` | `attendance_confirmation` | `participants/attendance_confirmation.html` | `app.js` | `confirm_attendance`, `sync_registration_to_team` | Participante | MU-009, MU-010 | Asistencia |
| P-09 Login interno | `/torneo/control/login/` | `LoginView` | `tournament/internal_login.html` | `app.js` | Django auth | Organizador | MU-012 | Acceso |
| P-10 Generar tablero | `/torneo/control/` | `control_dashboard` | `tournament/control_dashboard.html` | `control.js` | `initialize_competition`, `build_division_plan` | Operador torneo | MU-013, MU-014 | Operacion |
| P-11 Formato sugerido/manual | `/torneo/control/divisiones/<id>/` | `control_division` | `tournament/control_division.html` | `control.js` | `initialize_competition` | Operador torneo | MU-015, MU-016 | Configuracion |
| P-12 Distribucion manual | `/torneo/control/divisiones/<id>/` | `control_division` | `tournament/control_division.html` | `control.js` | `update_group_layout` | Operador torneo | MU-017 | Configuracion |
| P-13 Clasificados de grupos | `/torneo/control/divisiones/<id>/fases/groups/` | `control_division_stage` | `tournament/control_stage.html` | `control.js` | `set_group_qualifiers` | Operador torneo | MU-018, MU-019 | Fase grupos |
| P-14 Ganador de batalla | `/torneo/control/divisiones/<id>/fases/<stage>/` | `control_division_stage` | `tournament/control_stage.html` | `control.js` | `set_battle_winner` | Operador torneo | MU-026 | Batallas |
| P-15 Clasificados multiples | `/torneo/control/divisiones/<id>/fases/<stage>/` | `control_division_stage` | `tournament/control_stage.html` | `control.js` | `set_battle_qualifiers` | Operador torneo | MU-027 | Batallas |
| P-16 Guardado general | Misma fase | `control_division_stage` | `tournament/control_stage.html` | `control.js` | Servicios de resultados | Operador torneo | MU-020 | Guardado |
| P-17 Crear fase recomendada | Misma fase | `control_division_stage` | `control_stage.html`/`control_division.html` | `control.js` | `materialize_recommended_duel_stage` | Operador torneo | MU-021, MU-022 | Avance |
| P-18 Crear repechaje | Misma fase | `control_division_stage` | `control_stage.html`/`control_division.html` | `control.js` | `materialize_repechage_stage` | Operador torneo | MU-023 | Repechaje |
| P-19 Fase manual | Misma fase | `control_division_stage` | `_manual_phase_assistant.html` | `control.js` | `generate_manual_phase_proposal`, `confirm_manual_phase_proposal` | Operador torneo | MU-024, MU-025 | Fase manual |
| P-20 Correccion manual | Misma fase | `control_division_stage` | `control_stage.html` | `control.js` | `ManualCorrectionRequired`, servicios de resultados | Operador torneo | MU-028 | Correcciones |
| P-21 Modal participante | `/torneo/control/divisiones/<id>/participantes/<state_id>/` y `/actualizar/` | `participant_modal_detail`, `participant_modal_update` | `control_base.html` + render JS | `control.js` | `participant_modal_payload`, `update_participant_state` | Operador torneo | MU-029, MU-030 | Control manual |
| P-22 Podio final | `/torneo/control/divisiones/<id>/fases/final/` | `control_division_stage` | `tournament/control_stage.html` | `control.js` | `save_final_podium` | Operador torneo | MU-031 | Cierre |
| P-23 Plantillas | `/comunicaciones/plantillas/`, `/nueva/`, `/previsualizar/` | `template_list`, `template_create`, `template_preview` | `invitations/template_*.html` | `control.js` | `extract_docx_text_markers`, validadores | Operador comunicaciones | MU-033, MU-034, MU-035 | Plantillas |
| P-24 Destinatarios | `/comunicaciones/invitaciones/` | `invitations` | `invitations/invitations.html` | Script inline | `load_recipients_from_xlsx` | Operador comunicaciones | MU-036, MU-037 | Destinatarios |
| P-25 Invitaciones | `/comunicaciones/invitaciones/` | `invitations` | `invitations/invitations.html` | Script inline | `create_communication_batch`, `send_rendered_invitation` | Operador comunicaciones | MU-036 | Invitaciones |
| P-26 Confirmaciones | `/comunicaciones/confirmaciones/` | `confirmations` | `invitations/confirmations.html` | `control.js` | `send_attendance_request_for_registration` | Operador comunicaciones | MU-038 | Confirmaciones |
| P-27 Historial | `/comunicaciones/historial/` | `history` | `invitations/history.html` | `control.js` | Modelos `CommunicationBatch`, `CommunicationLog` | Operador comunicaciones | MU-039 | Historial |
| P-28 Django Admin | `/admin/` | Django Admin | Admin Django | No aplica | Admin actions y modelos | Superusuario | MU-040, MU-041, MU-042 | Administracion |

Esta matriz permite comprobar que cada procedimiento propuesto corresponde con rutas, vistas, plantillas o servicios reales observados en el proyecto.
