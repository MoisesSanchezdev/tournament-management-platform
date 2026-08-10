# 17. Migraciones

## Migraciones detectadas

| App | Migraciones |
| --- | --- |
| `common` | `__init__.py` |
| `core` | `__init__.py` |
| `participants` | `0001_initial.py` a `0008_universityregistration_semester.py` |
| `tournament` | `0001_initial.py` a `0005_competitionhistoryentry_teamcompetitionstate.py` |
| `invitations` | `0001_initial.py`, `0002_batch_send_mode_and_log_recipients.py` |

## Evolucion `participants`

| Migracion | Cambio confirmado por nombre/contenido |
| --- | --- |
| `0001_initial` | Instituciones, equipos y miembros iniciales |
| `0002_initial` | Relaciones iniciales complementarias |
| `0003_schoolregistration_schoolparticipant_and_more` | Registros escolares/universitarios y participantes |
| `0004_align_registration_form` | Alineacion de formulario de registro |
| `0005_alter_schoolparticipant_role_and_more` | Ajustes de roles |
| `0006_schoolregistration_unique_school_robot_registration_and_more` | Unicidad de robot por edicion/institucion |
| `0007_registration_attendance_workflow` | Tokens y flujo de asistencia |
| `0008_universityregistration_semester` | Campo `semester` |

## Evolucion `tournament`

| Migracion | Cambio confirmado |
| --- | --- |
| `0001_initial` | Edicion, reglas, fases y matches |
| `0002_divisioncompetition_competitionbattle_divisiongroup_and_more` | Competencia por division, grupos, batallas y entries |
| `0003_divisioncompetition_configuration_and_more` | Configuracion JSON y ajustes asociados |
| `0004_divisiongroupentry_qualified_from_group` | Clasificacion desde grupos |
| `0005_competitionhistoryentry_teamcompetitionstate` | Historial y estado por equipo |

## Evolucion `invitations`

| Migracion | Cambio confirmado |
| --- | --- |
| `0001_initial` | Plantillas, destinatarios, lotes y logs |
| `0002_batch_send_mode_and_log_recipients` | Modo de envio y correos fisicos/originales en logs |

## Estado de ejecucion

No se ejecuto `migrate`, `makemigrations` ni se modifico la base de datos durante esta auditoria.

`manage.py check` con `.venv` reporto cero issues, pero no confirma que todas las migraciones esten aplicadas en cada ambiente.

## Riesgos

| Riesgo | Evidencia |
| --- | --- |
| Migraciones no validadas contra produccion | No hay evidencia de ambiente productivo |
| Cambios JSON en `configuration` | Parte de la logica depende de claves dinamicas no fuertemente tipadas |
| Comando demo destructivo | Puede borrar datos aunque no sea migracion |

## Recomendaciones

1. Antes de despliegue, ejecutar `python manage.py showmigrations` y registrar salida por ambiente.
2. Respaldar base antes de aplicar migraciones.
3. Documentar estructura esperada de `DivisionCompetition.configuration`.
