# 06. URLs

## URL raiz

Fuente: `config/urls.py`

| Ruta | Include/Vista |
| --- | --- |
| `/admin/` | Django admin |
| `/` | `apps.core.urls` |
| `/registro/` | `apps.participants.urls` |
| `/comunicaciones/` | `apps.invitations.urls` |
| `/torneo/` | `apps.tournament.urls` |
| `/media/` | Solo si `settings.DEBUG` |

## App `core`

| Ruta | Nombre | Vista |
| --- | --- | --- |
| `/` | `core:home` | `home` |
| `/reglas/` | `core:rules` | `rules_page` |
| `/patrocinadores/` | `core:sponsors` | `sponsors_page` |

## App `participants`

| Ruta | Nombre | Vista |
| --- | --- | --- |
| `/registro/` | `participants:team_register` | `registration_choice` |
| `/registro/colegios/` | `participants:school_register` | `school_register` |
| `/registro/universidades/` | `participants:university_register` | `university_register` |
| `/registro/exito/<registration_type>/` | `participants:registration_success` | `registration_success` |
| `/registro/confirmar-asistencia/<uuid:token>/` | `participants:attendance_confirmation` | `attendance_confirmation` |

## App `tournament`

| Ruta | Nombre | Vista |
| --- | --- | --- |
| `/torneo/` | `tournament:overview` | `overview` |
| `/torneo/control/login/` | `tournament:control_login` | `LoginView` |
| `/torneo/control/logout/` | `tournament:control_logout` | `LogoutView` |
| `/torneo/control/` | `tournament:control_dashboard` | `control_dashboard` |
| `/torneo/control/divisiones/<competition_id>/` | `tournament:control_division` | `control_division` |
| `/torneo/control/divisiones/<competition_id>/fases/<stage_key>/` | `tournament:control_division_stage` | `control_division_stage` |
| `/torneo/control/divisiones/<competition_id>/participantes/<state_id>/` | `tournament:participant_modal_detail` | `participant_modal_detail` |
| `/torneo/control/divisiones/<competition_id>/participantes/<state_id>/actualizar/` | `tournament:participant_modal_update` | `participant_modal_update` |
| `/torneo/control/fases/<phase_id>/` | `tournament:control_phase_detail` | `control_phase_detail` |

## App `invitations`

| Ruta | Nombre | Vista |
| --- | --- | --- |
| `/comunicaciones/` | `invitations:dashboard` | `dashboard` |
| `/comunicaciones/plantillas/` | `invitations:template_list` | `template_list` |
| `/comunicaciones/plantillas/nueva/` | `invitations:template_create` | `template_create` |
| `/comunicaciones/plantillas/<template_id>/previsualizar/` | `invitations:template_preview` | `template_preview` |
| `/comunicaciones/invitaciones/` | `invitations:invitations` | `invitations` |
| `/comunicaciones/confirmaciones/` | `invitations:confirmations` | `confirmations` |
| `/comunicaciones/historial/` | `invitations:history` | `history` |

## Proteccion de rutas

| Area | Proteccion confirmada |
| --- | --- |
| Publica core | Sin decoradores de auth |
| Registro participantes | Sin decoradores de auth |
| Confirmacion por token | Token UUID, sin login |
| Panel torneo | `login_required` + `user_passes_test(is_organizer)` |
| Comunicaciones | `login_required` + `user_passes_test(is_organizer)` |

`is_organizer` valida usuario autenticado y `is_staff` o `is_superuser`.
