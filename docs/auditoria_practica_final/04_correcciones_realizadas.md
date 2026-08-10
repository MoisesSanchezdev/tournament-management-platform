# 04. Correcciones realizadas

No se modificaron modelos ni migraciones. Las correcciones fueron localizadas y conservaron la compatibilidad con las competencias existentes.

| Archivo | Cambio | Justificación | Prueba asociada | Resultado / efecto secundario |
| --- | --- | --- | --- | --- |
| `apps/tournament/services.py` | Bloqueo de la competencia antes de guardar grupos, batallas, podio, inicialización y materialización de fases | Evitar escrituras perdidas sobre `configuration` y ordenar bloqueos | Pestaña obsoleta, repetición de solicitudes, suite integral | Guardados consistentes; las correcciones reales requieren confirmación |
| `apps/tournament/services.py` | Idempotencia para resultados de grupo, ganador único y clasificados múltiples | Reintentos AJAX y doble clic no deben duplicar historial | `test_repeated_winner_request_is_idempotent`, `test_repeated_group_and_multi_qualifier_requests_are_idempotent` | Repetir el mismo payload no altera el estado |
| `apps/tournament/services.py` | Reemplazo de participantes afectados en la primera fase dependiente | Corregir llaves obsoletas sin destruir resultados paralelos | Correcciones de grupo, campal, semifinal y corrección profunda | Se invalida solo la rama incompatible |
| `apps/tournament/services.py` | Limpieza de resultados posteriores, configuración progresiva, plan pendiente y podio al corregir | Evitar final/podio incoherentes | `test_semifinal_correction_invalidates_saved_podium_and_downstream_results` | La competencia puede reconstruirse hasta un nuevo podio |
| `apps/tournament/services.py` | Selección de repechables excluye participantes usados previamente | Impedir dos oportunidades de repechaje para el mismo equipo | Pruebas de uno/dos repechajes y P2 inmediato | P2 sigue disponible con candidatos realmente nuevos |
| `apps/tournament/recommendations.py` | La vista previa aplica la misma exclusión de repechaje que el servicio | La interfaz no debe ofrecer una acción que el backend rechazará | `test_second_repechage_cannot_immediately_reuse_first_repechage_participants` | Recomendación y ejecución quedan alineadas |
| `apps/tournament/services.py` | El cierre espera el tercer lugar y valida podio único | Garantizar campeón, subcampeón y tercero correctos | `test_standard_podium_waits_for_third_place_and_contains_three_unique_teams` | No se completa prematuramente |
| `apps/participants/services.py` | Sincronización atómica, bloqueo de competencia y rechazo de altas tardías incompatibles | Evitar equipos aprobados pero excluidos y carreras de sincronización | `test_new_approved_team_is_not_silently_excluded_after_progress` | El operador recibe un error explícito antes de continuar |
| `apps/participants/services.py` | Prohibición de cambiar silenciosamente el tipo de una institución existente | Conservar separación C/U | `test_shared_institution_name_cannot_change_category_silently` | Requiere resolución explícita del dato |
| `apps/participants/forms.py` | Guardado de inscripción y sincronización dentro de transacción | Evitar una inscripción parcialmente sincronizada | Suite completa | Rollback conjunto ante error |
| `apps/tournament/views.py` | Validación de que grupo/batalla pertenezca a la competencia y errores JSON | Corregir contratos AJAX para IDs vacíos o cruzados | Pruebas HTTP 400 y JSON | No se filtra una página HTML 404 al JavaScript |
| `apps/tournament/views.py` | HTTP 409 para correcciones que requieren confirmación | Advertir antes de alterar progreso | `test_ajax_manual_correction_uses_409_confirmation_contract` | Cancelar no modifica datos; confirmar usa `manual_override` |
| `apps/tournament/views.py`, `apps/tournament/urls.py`, `static/js/control.js` | Retiro de la edición manual arbitraria desde el modal | La acción no recalculaba dependencias | `test_removed_manual_move_route_is_not_accessible` y validación visual | Modal queda de solo lectura e historial |
| `apps/tournament/views.py`, `control_division.html`, `control_stage.html` | Estado de cierre explícito y sin acción de avance | Evitar recomendación contradictoria tras guardar el podio | `test_completed_tournament_hides_phase_advance_action` | Se muestra “Torneo finalizado” |
| `apps/tournament/management/commands/reset_tournament_demo.py` | Doble barrera: setting aislado y bandera CLI | Impedir un reinicio de demostración contra datos reales | Tres pruebas de seguridad del comando | En producción falla antes de borrar |
| `config/audit_settings.py` | Configuración SQLite temporal y marca destructiva solo para auditoría | Ejecutar pruebas sin tocar PostgreSQL real | 46 pruebas | No participa en la configuración normal |
| `docs/manual_usuario/herramientas/demo_settings.py` | Marca explícita para el entorno de demostración documentado | Conservar la herramienta de demo bajo una configuración aislada | Prueba de comando confirmado | La herramienta sigue disponible de forma deliberada |
| `apps/tournament/test_audit.py` | 34 pruebas funcionales y de seguridad | Convertir los fallos reproducidos en regresiones permanentes | `manage.py test` | 34/34 dentro de la suite total |
| `apps/invitations/tests.py` | Ajuste del mock de ruta de LibreOffice | Hacer las pruebas de invitación independientes de la instalación local | Suite total | No cambia la lógica productiva |

## Validaciones después de los cambios

- Suite total: 46/46 pruebas exitosas.
- `manage.py check`: 0 incidencias.
- `makemigrations --check --dry-run`: sin cambios.
- `pip check`: sin dependencias rotas.
- `git diff --check`: sin errores de espacios; solo avisos de conversión LF/CRLF de Git en Windows.
- Inicio temporal del servidor: respuesta HTTP 200.
- Interfaz integral aislada: torneo de Colegios completado y Universidades intacto.
- Base real: consultas de integridad en transacción de solo lectura, 0 infracciones en las reglas auditadas.

## Posibles efectos secundarios controlados

- Una corrección de un resultado ya guardado ahora siempre exige confirmación, incluso si aún no se creó la fase siguiente. Es deliberado para proteger frente a pestañas obsoletas.
- Una corrección profunda elimina resultados posteriores incompatibles; el mensaje advierte la consecuencia y los resultados paralelos no afectados se conservan.
- Aprobar equipos después de iniciar una competencia puede bloquear la sincronización hasta resolver la discrepancia. Es preferible a excluir al equipo silenciosamente.
- Un segundo repechaje no puede abrirse inmediatamente con los mismos participantes; requiere candidatos que no hayan disputado P1/P2.
- El comando de demo deja de funcionar con la configuración normal. Debe usarse únicamente con las dos confirmaciones de seguridad.
