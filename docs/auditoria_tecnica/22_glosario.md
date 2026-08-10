# 22. Glosario

| Termino | Definicion en el proyecto |
| --- | --- |
| Edicion | Instancia de `TournamentEdition` que agrupa reglas, registros, equipos y competencias |
| Division | Categoria operativa: `school`/Colegios o `university`/Universidades |
| Registro | Inscripcion publica en `SchoolRegistration` o `UniversityRegistration` |
| Participante | Persona integrante de un registro escolar/universitario |
| Institucion | Entidad educativa modelada en `Institution` |
| Equipo | Robot/equipo operativo modelado en `Team` |
| Miembro | Integrante operativo de un `Team` |
| Competencia por division | `DivisionCompetition`, tablero operativo para una division |
| Perfil de competencia | Diccionario de configuracion generado por `competition_profile` |
| Grupo | `DivisionGroup`, agrupacion inicial de equipos |
| Entry de grupo | `DivisionGroupEntry`, equipo dentro de grupo con slot y clasificacion |
| Clasificado de grupo | Entry con `qualified_from_group=True` |
| Batalla | `CompetitionBattle`, enfrentamiento o campal por etapa |
| Entry de batalla | `CompetitionBattleEntry`, equipo dentro de una batalla |
| Stage | Valor de `CompetitionStage` que identifica fase operativa |
| Purgatorio | Repechaje modelado como `purgatory_1` o `purgatory_2` |
| Repechaje | Via de recuperacion de participantes eliminados/repechables |
| Estado de participante | `TeamCompetitionState`, posicion actual de un equipo |
| Historial | `CompetitionHistoryEntry`, registro de movimientos/resultados |
| Manual override | Confirmacion para aplicar correcciones que afectan fases posteriores |
| Fase manual | Fase creada por propuesta manual de grupos/duelos/repechaje |
| Propuesta manual | Estructura temporal guardada en `configuration["manual_phase_proposal"]` |
| Podio | Resultado final guardado en `configuration["final_podium"]` |
| Dry-run | Simulacion que registra logs sin enviar correo real |
| Prueba controlada | Envio fisico a correo de prueba, no al destinatario original |
| Envio oficial | Envio real a destinatarios finales |
| Plantilla DOCX | Archivo cargado en `CommunicationTemplate` |
| Marcador | Placeholder tipo `{{NOMBRE}}` usado en DOCX |
| Lote | `CommunicationBatch`, conjunto de envios |
| Log de comunicacion | `CommunicationLog`, resultado por destinatario |
