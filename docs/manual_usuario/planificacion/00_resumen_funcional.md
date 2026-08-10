# Resumen funcional

## Sistema revisado

La plataforma es una aplicacion Django para publicar informacion del torneo Robot Explota Globos, registrar participantes, confirmar asistencia, operar competencias por division y gestionar comunicaciones internas.

| Dominio | Evidencia | Funcion para usuario |
| --- | --- | --- |
| Sitio publico | `apps.core` | Inicio, reglas, patrocinadores y enlaces de registro. |
| Registro | `apps.participants` | Formularios de colegios/universidades y confirmacion por token. |
| Torneo | `apps.tournament` | Panel interno, divisiones, grupos, batallas, repechajes, fases manuales, podio e historial. |
| Comunicaciones | `apps.invitations` | Plantillas DOCX, destinatarios, lotes, confirmaciones e historial de envios. |
| Administracion | `admin.py` de cada app y `/admin/` | Mantenimiento de modelos y acciones administrativas. |

## Roles reales

El sistema implementa permisos formales basados en autenticacion Django:

- visitante publico: no autenticado;
- participante o responsable de registro: no autenticado, usa formulario publico o enlace con token;
- usuario organizador: usuario autenticado con `is_staff` o `is_superuser`;
- superusuario de Django Admin: usuario con acceso total al Admin.

Las figuras "operador del torneo" y "operador de invitaciones" son funciones operativas realizadas por usuarios organizadores. No aparecen como roles independientes en el codigo.

## Flujos principales

1. Consulta publica: inicio, reglas, patrocinadores y fases publicas.
2. Registro: seleccion de categoria, formulario escolar o universitario, validaciones y confirmacion visual.
3. Asistencia: enlace con token, confirmacion y sincronizacion hacia equipo operativo.
4. Torneo: generacion de competencia, configuracion, grupos, batallas, repechajes, fases manuales, correcciones y podio.
5. Comunicaciones: plantillas, destinatarios, lotes, solicitudes de asistencia e historial.
6. Admin: ediciones, reglas, registros, equipos, competencias, estados, plantillas, destinatarios, lotes y logs.

## Estado de datos demo

El repositorio contiene capturas existentes en `docs/screenshots/` descritas como simulaciones. Sin embargo, no se verifico una base de datos temporal segura para nuevas capturas y no se ejecuto ningun comando de siembra.

Resultado: **PENDIENTE DE PREPARAR DATOS DE DEMOSTRACION**.

## Observaciones criticas

- El comando `reset_tournament_demo.py` elimina datos operativos antes de sembrar simulacion. Es riesgo alto y no debe ejecutarse sobre datos reales.
- Las operaciones de torneo escriben estado persistente; las capturas futuras deben hacerse en una base temporal.
- Las pantallas internas pueden exponer nombres, correos, documentos, tokens o instituciones reales.
- El Manual de Usuario debe ser visual y operativo, no repetir el Manual Tecnico.
