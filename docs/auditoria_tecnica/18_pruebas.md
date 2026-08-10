# 18. Pruebas

## Archivos de prueba detectados

| Archivo | Cobertura |
| --- | --- |
| `apps/tournament/tests.py` | Distribuciones manuales de fase |
| `apps/invitations/tests.py` | Conversion PDF, adjuntos y envio de invitaciones |
| `apps/participants` | No se detectan pruebas dedicadas |
| `apps/core` | No se detectan pruebas dedicadas |

## `apps/tournament/tests.py`

| Test | Verifica |
| --- | --- |
| `test_exact_distributions_for_36_cover_requested_formats` | Opciones exactas para 36 participantes |
| `test_exact_distributions_for_10_do_not_offer_trios` | No ofrece trios si no cubren todos los participantes |
| `test_balanced_custom_distribution_for_17_in_4_groups` | Distribucion balanceada `[5, 4, 4, 4]` |

## `apps/invitations/tests.py`

| Clase | Cobertura |
| --- | --- |
| `PDFConversionTests` | Conversion PDF, ausencia de LibreOffice, timeout, PDF faltante, sanitizacion de filename, MIME |
| `InvitationEmailTests` | Adjuntar PDF sin DOCX, limpieza de temporales, fallo de conversion no marca enviado |

## Validacion ejecutada en auditoria

| Comando | Resultado |
| --- | --- |
| `.venv\Scripts\python.exe manage.py check` | `System check identified no issues (0 silenced).` |

No se ejecutaron tests completos para evitar crear bases de prueba o modificar estado operativo.

## Gaps de cobertura

| Area | Estado |
| --- | --- |
| Modelos de participantes | Sin pruebas detectadas |
| Formularios de registro | Sin pruebas detectadas |
| Confirmacion de asistencia | Sin pruebas detectadas |
| Inicializacion completa de competencia | Sin pruebas integrales detectadas |
| Vistas del panel | Sin pruebas detectadas |
| AJAX `control.js` | Sin pruebas frontend detectadas |
| Seguridad/permisos | Sin pruebas detectadas |
| Comandos de gestion | Pruebas no detectadas |

## Recomendaciones

1. Agregar pruebas para `BaseRegistrationForm` con duplicados de robot, correo y documento.
2. Agregar pruebas para `confirm_attendance` y sincronizacion a `Team`.
3. Agregar pruebas para `initialize_competition`, `set_group_qualifiers`, `set_battle_winner` y `save_final_podium`.
4. Agregar pruebas de permisos para panel interno y comunicaciones.
5. Agregar pruebas de comandos en dry-run para invitaciones y asistencia.
