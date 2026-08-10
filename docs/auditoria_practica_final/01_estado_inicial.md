# 01. Estado inicial y salvaguardas

## Identificación

- Fecha de auditoría: 27 de julio de 2026.
- Zona horaria de referencia: America/Bogota.
- Proyecto auditado: `C:\Projects\pre_explotaglobos`.
- Se confirmó que el trabajo se realizó en `C:\Projects`, no en la copia de OneDrive.
- Rama: `final-fases-repechaje-manual`.
- Commit base: `5988e9ea1ae3bc32af37f08fa04cddf9c0732375`.
- Último commit: `Complete manual phase assistant and improve tournament UI`.
- No se hizo `commit`, `push`, `merge`, `reset`, cambio de rama ni publicación.

## Estado de Git preservado

El repositorio ya contenía documentación no rastreada y trabajo de auditoría previo. El primer registro verificable del proceso reportó archivos rastreados limpios y 285 archivos no rastreados, principalmente documentación. Al retomar la auditoría también existían cambios locales relacionados con pruebas y seguridad del torneo. Todos se preservaron y se incluyeron en la copia integral previa a las correcciones adicionales.

Estado final de trabajo, sin confirmar:

- Modificados: pruebas de invitaciones; formularios y servicios de participantes; comando de demostración; recomendaciones, servicios, vistas, URLs y plantillas del torneo; JavaScript de control.
- Nuevos: configuración aislada de auditoría, pruebas prácticas del torneo y documentación.
- No se alteró el historial de Git.

## Entorno

- Intérprete: `C:\Projects\pre_explotaglobos\.venv\Scripts\python.exe`.
- Python: 3.12.10, 64 bits.
- Django: 5.2.16.
- Dependencias: `pip check` sin requisitos rotos.
- Base de datos configurada por el proyecto: PostgreSQL.
- Base de datos real: `robot_tournament`.
- PostgreSQL: `server_version_num = 180003` (18.3).
- `python manage.py check`: 0 incidencias.
- `python manage.py makemigrations --check --dry-run`: no se detectaron cambios de modelos.

## Copias de seguridad verificadas

### Respaldo lógico y de Git

Ruta: `C:\Projects\pre_explotaglobos_audit_backups\20260727_192830`

- `robot_tournament.pgcustom`: 162.587 bytes.
- SHA-256: `6F9E77C7BA800E8167765D37A93F1663F669CD6C268DAFAA294F9DB501DDFD4C`.
- `pg_restore --list`: 311 entradas, lectura correcta.
- `tracked_repository.bundle`: 12.871.029 bytes.
- SHA-256: `0C5EF5A20C522809D451FCCD5BDE52FDE75862B25E35EB9D321F8DE8C6E289C7`.
- `git bundle verify`: historial completo y válido; contiene la rama y el commit base.

### Instantánea integral de archivos

Ruta: `C:\Projects\pre_explotaglobos_audit_backups\20260727_195743`

- Copia del árbol del proyecto, incluida `.git` y los archivos no rastreados.
- Exclusiones deliberadas: entornos virtuales y cachés regenerables.
- Verificación en el momento de creación: 2.106 archivos y 136.140.894 bytes en origen y destino.
- Copia de `db.sqlite3`: SHA-256 `62A174E0E49D7EA17FCD8C7E756527FA57AEC726EA7B50EAB615D2B2F787FFEC`.
- `PRAGMA integrity_check` sobre la copia SQLite: `ok`.

La base SQLite del repositorio no es la base activa del sistema; se conservó porque forma parte del árbol. Las pruebas destructivas se hicieron únicamente sobre bases SQLite temporales dentro de la carpeta de respaldos.

## Estado de los datos reales

La consulta final se ejecutó dentro de una transacción PostgreSQL marcada `READ ONLY`.

| Elemento | Cantidad |
| --- | ---: |
| Ediciones | 1 |
| Ediciones activas | 1 |
| Inscripciones de colegios | 74 |
| Inscripciones de universidades | 50 |
| Equipos sincronizados | 123 |
| Competencias | 2 |
| Asignaciones de grupo | 123 |
| Asignaciones a batallas | 0 |
| Estados de competencia | 123 |
| Entradas de historial | 0 |

Detalle:

- Colegios: competencia 3, borrador, 73 equipos, 16 grupos, 73 asignaciones, sin batallas iniciadas.
- Universidades: competencia 4, borrador, 50 equipos, 8 grupos, 24 batallas precreadas sin participantes ni resultados.
- Colegios usa perfil manual: nueve grupos de 5 y siete de 4, dos clasificados por grupo, 32 clasificados; Purgatorio 1 habilitado y Purgatorio 2 deshabilitado.
- Universidades usa perfil `explosion_standard`: grupos de 7, 7 y seis grupos de 6; 16 clasificados. Conserva el motor heredado, con Purgatorio 1 y 2 configurados.

No cambiaron los conteos reales durante la auditoría. Se encontraron cero infracciones en las consultas de duplicidad por grupo o fase, ganador ajeno a batalla, batalla finalizada sin ganador, referencia cruzada de competencia, equipo presente en ambas categorías, final con más de dos participantes y podio duplicado o incompleto.

## Flujo reconstruido

1. Una inscripción aprobada de colegio o universidad se sincroniza con `Institution`, `Team` y sus miembros.
2. `initialize_competition()` selecciona exclusivamente los equipos de la edición y categoría solicitadas.
3. El perfil automático o manual define número de grupos, cupos y fases permitidas.
4. La asignación a grupos se distribuye con tamaños balanceados y crea un único estado por equipo y competencia.
5. Los resultados de grupo marcan clasificados y eliminados; la corrección usa confirmación explícita.
6. El motor progresivo materializa únicamente la fase siguiente. El motor heredado conserva batallas precreadas para configuraciones antiguas.
7. Los ganadores o clasificados de cada batalla actualizan su estado y su historial.
8. Los repechajes seleccionan eliminados elegibles que no hayan participado en repechajes anteriores.
9. Una corrección reemplaza al participante afectado en la primera fase dependiente, invalida resultados posteriores incompatibles y conserva resultados paralelos no relacionados.
10. Final y tercer lugar alimentan un podio de tres equipos únicos; el torneo solo queda completado cuando los resultados requeridos están cerrados y el podio se guarda.

## Riesgos iniciales priorizados

- Correcciones tardías podían dejar participantes obsoletos en semifinal, final o podio.
- Una petición repetida o una segunda pestaña podía sobrescribir un resultado sin confirmación.
- El mismo participante podía reciclarse en ambos repechajes progresivos.
- La acción administrativa de mover participantes arbitrariamente entre fases no recalculaba todas las dependencias.
- El comando de reinicio de demostración podía borrar datos si se ejecutaba contra una configuración equivocada.
- Una aprobación tardía podía quedar fuera de una competencia ya iniciada sin una explicación suficientemente estricta.
- La coexistencia de motores progresivo y heredado requería validar ambos.
- La configuración de despliegue conserva opciones inseguras para una exposición pública: `DEBUG=True`, clave débil y ausencia de HTTPS/cookies seguras.
