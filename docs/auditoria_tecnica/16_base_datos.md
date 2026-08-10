# 16. Base de datos

## Motores soportados

| Motor | Condicion |
| --- | --- |
| SQLite | `DJANGO_DATABASE=sqlite` o debug sin PostgreSQL |
| PostgreSQL | Cuando no se usa SQLite y existen variables `POSTGRES_*` requeridas |

## Archivo local

Se detecta `db.sqlite3` en la raiz del proyecto. `.gitignore` lo excluye.

## Politica SQLite

Si `USE_SQLITE=True` y `DEBUG=False`, se lanza `ImproperlyConfigured`.

## Modelos persistidos por dominio

| Dominio | Modelos |
| --- | --- |
| Participantes | `SchoolRegistration`, `UniversityRegistration`, `SchoolParticipant`, `UniversityParticipant`, `Institution`, `Team`, `TeamMember` |
| Torneo | `TournamentEdition`, `RuleSection`, `TournamentPhase`, `Match`, `DivisionCompetition`, `DivisionGroup`, `DivisionGroupEntry`, `CompetitionBattle`, `CompetitionBattleEntry`, `TeamCompetitionState`, `CompetitionHistoryEntry` |
| Comunicaciones | `CommunicationTemplate`, `CommunicationRecipient`, `CommunicationBatch`, `CommunicationLog` |

## Integridad referencial

| Relacion | Politica |
| --- | --- |
| Registro a edicion | `PROTECT` |
| Team a edicion | `PROTECT` |
| Team a institucion | `PROTECT` |
| Grupos/batallas a competencia | `CASCADE` |
| Entries a grupo/batalla | `CASCADE` |
| Battle winner a team | `PROTECT` |
| Historial a grupos/batallas | `SET_NULL` en referencias historicas opcionales |

## Indices y restricciones

1. Edicion activa unica.
2. Competencia unica por edicion/division.
3. Grupo unico por label y order dentro de competencia.
4. Entry unico por equipo y slot dentro de grupo.
5. Ranking unico no nulo por grupo.
6. Batalla unica por competencia/stage/order.
7. Entry unico por equipo y slot dentro de batalla.
8. Estado unico por competencia/equipo.
9. Match evita `team_a == team_b`.
10. Indices sobre status, fechas, documentos, tipos de comunicacion y logs.

## Datos operativos relevantes

| Dato | Ubicacion |
| --- | --- |
| Podio final | `DivisionCompetition.configuration["final_podium"]` |
| Perfil de competencia | `DivisionCompetition.configuration` |
| Propuesta manual pendiente | `DivisionCompetition.configuration["manual_phase_proposal"]` |
| Planes de integracion | `DivisionCompetition.configuration` |
| Preview de comunicaciones | `CommunicationLog.rendered_preview` |

## No confirmado

| Punto | Estado |
| --- | --- |
| Volumen real de datos | NO CONFIRMADO |
| Backups de produccion | NO CONFIRMADO |
| Politica de retencion | NO CONFIRMADO |
| Migracion de SQLite a PostgreSQL ejecutada | NO CONFIRMADO |
