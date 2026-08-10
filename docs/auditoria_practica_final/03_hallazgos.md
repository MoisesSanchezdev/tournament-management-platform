# 03. Hallazgos

## H-01 — Clasificado obsoleto después de corregir grupos

- Severidad: crítica.
- Escenario: corregir un clasificado de grupo después de materializar semifinal.
- Resultado previo: el equipo retirado podía permanecer en semifinal y el nuevo clasificado no ocupar su lugar.
- Causa raíz: la corrección actualizaba el estado inmediato, pero no reemplazaba de forma determinista las asignaciones dependientes.
- Riesgo: llave incorrecta y participante legítimo excluido.
- Archivos: `apps/tournament/services.py`, `apps/tournament/test_audit.py`.
- Solución: reemplazar participantes retirados/agregados en la primera fase dependiente e invalidar únicamente la rama posterior incompatible.
- Estado: corregido y probado.

## H-02 — Corrección campal con clasificados obsoletos

- Severidad: crítica.
- Escenario: cambiar varios clasificados en una batalla de formato múltiple.
- Resultado previo: una semifinal ya creada podía retener participantes que dejaron de clasificar.
- Causa raíz: la lógica de reemplazo estaba orientada al ganador único.
- Riesgo: avances duplicados o cuadro formado con perdedores.
- Archivos: `apps/tournament/services.py`.
- Solución: comparar conjuntos anterior/nuevo y aplicar el reemplazo para todos los participantes afectados.
- Estado: corregido y probado.

## H-03 — Podio y final no invalidados por una corrección tardía

- Severidad: crítica.
- Escenario: corregir una semifinal después de guardar final, tercer lugar o podio.
- Resultado previo: `final_podium` podía seguir nombrando al campeón anterior.
- Causa raíz: la corrección no borraba toda la configuración derivada de fases posteriores.
- Riesgo: podio oficialmente incorrecto aunque la semifinal visible hubiese sido corregida.
- Archivos: `apps/tournament/services.py`.
- Solución: limpiar resultados posteriores dependientes, configuración de clasificados, plan pendiente y podio; devolver la competencia a un estado reconstruible.
- Estado: corregido y probado hasta un nuevo podio válido.

## H-04 — Reutilización del mismo participante en dos repechajes

- Severidad: alta.
- Escenario: abrir Purgatorio 2 inmediatamente después de Purgatorio 1.
- Resultado previo: los perdedores recientes del primer repechaje podían volver a aparecer como candidatos.
- Causa raíz: el cálculo solo observaba el estado actual y no el historial de entradas a repechaje.
- Riesgo: ventaja competitiva injusta y participante duplicado conceptualmente.
- Archivos: `apps/tournament/recommendations.py`, `apps/tournament/services.py`.
- Solución: excluir todos los equipos que ya tengan una entrada en P1 o P2; no ofrecer P2 sin candidatos nuevos.
- Estado: corregido y probado. Dos repechajes siguen siendo posibles cuando existe una ronda normal intermedia y candidatos distintos.

## H-05 — Sobrescritura desde una segunda pestaña

- Severidad: alta.
- Escenario: dos pestañas cargan el mismo resultado; la primera guarda y la segunda intenta guardar una selección antigua.
- Resultado previo: la segunda petición podía sobrescribir el resultado sin una nueva confirmación.
- Causa raíz: la confirmación solo se exigía cuando ya existía una fase posterior.
- Riesgo: cambio accidental de ganador durante operación en vivo.
- Archivos: `apps/tournament/services.py`, `apps/tournament/views.py`.
- Solución: cualquier cambio de un resultado ya guardado exige `manual_override`; una repetición idéntica continúa siendo idempotente.
- Estado: corregido; contrato HTTP 409 validado.

## H-06 — Riesgo de actualización perdida en configuración JSON

- Severidad: alta.
- Escenario: guardados concurrentes modifican resultados y `configuration`.
- Causa raíz: se bloqueaba el grupo o la batalla, pero no siempre la fila de `DivisionCompetition` que contiene el JSON compartido.
- Riesgo: pérdida de metadatos de fase o podio por escritura de una versión antigua.
- Archivos: `apps/tournament/services.py`, `apps/participants/services.py`.
- Solución: bloquear primero la competencia con `select_for_update()` y mantener un orden de bloqueo consistente.
- Estado: corregido por diseño y cubierto por regresiones de pestaña obsoleta. La concurrencia real sobre PostgreSQL queda como observación porque el usuario de pruebas no puede crear una base de test.

## H-07 — Equipo aprobado tarde podía quedar fuera silenciosamente

- Severidad: alta.
- Escenario: aprobar o sincronizar un nuevo equipo cuando la competencia ya tiene progreso.
- Causa raíz: el andamiaje existente no podía incorporar un equipo sin recalcular grupos/resultados.
- Riesgo: participante aprobado pero ausente del torneo.
- Archivos: `apps/participants/services.py`, `apps/tournament/services.py`.
- Solución: transacción atómica y error explícito que exige resolver la discrepancia antes de continuar.
- Estado: corregido y probado.

## H-08 — Movimiento manual arbitrario entre fases

- Severidad: alta.
- Escenario: mover un participante a una fase, grupo, batalla o estado desde el modal.
- Causa raíz: la acción modificaba el estado individual sin reconstruir entradas, rivales, ganadores ni fases dependientes.
- Riesgo: estado visual aparentemente válido con una llave internamente corrupta.
- Archivos: `apps/tournament/views.py`, `apps/tournament/urls.py`, `static/js/control.js`.
- Solución: retirar controles, endpoint y ruta. El modal conserva consulta de estado e historial.
- Estado: retirado; la ruta devuelve 404 y no quedan botones operativos.

## H-09 — Reinicio de demostración insuficientemente protegido

- Severidad: alta.
- Escenario: ejecutar `reset_tournament_demo` con la configuración principal por error.
- Causa raíz: el comando destructivo no exigía una marca de entorno aislado y una confirmación de CLI simultáneas.
- Riesgo: borrado masivo de datos reales.
- Archivos: `apps/tournament/management/commands/reset_tournament_demo.py`, `config/audit_settings.py`, `docs/manual_usuario/herramientas/demo_settings.py`.
- Solución: exigir `ALLOW_DESTRUCTIVE_DEMO_RESET=True` y `--confirm-demo-reset`.
- Estado: corregido; tres pruebas validan bloqueo y uso aislado.

## H-10 — Finalización prematura y tercer lugar

- Severidad: alta.
- Escenario: guardar la final antes de completar el duelo por tercer lugar.
- Resultado previo: existía riesgo de marcar la competencia terminada o inferir mal el tercero.
- Causa raíz: el cierre no trataba el tercer lugar como dependencia obligatoria cuando estaba habilitado.
- Riesgo: podio incompleto o tercero equivocado.
- Archivos: `apps/tournament/services.py`.
- Solución: esperar el tercer lugar, inferir campeón/segundo/tercero desde batallas terminadas y exigir tres equipos únicos.
- Estado: corregido y probado.

## H-11 — Cambio silencioso de categoría de una institución compartida

- Severidad: media.
- Escenario: sincronizar una inscripción cuyo nombre de institución ya existe con otro tipo.
- Causa raíz: la sincronización podía reutilizar y mutar la institución compartida.
- Riesgo: mezclar indirectamente colegios y universidades.
- Archivos: `apps/participants/services.py`, `apps/participants/forms.py`.
- Solución: impedir el cambio silencioso y ejecutar la sincronización en transacción atómica.
- Estado: corregido y probado.

## H-12 — Respuestas AJAX inconsistentes para objetos ajenos

- Severidad: media.
- Escenario: enviar a una competencia el ID de un grupo o batalla perteneciente a otra.
- Resultado previo: podía devolverse una respuesta HTML 404 en un flujo que espera JSON.
- Riesgo: JavaScript bloqueado o mensaje incomprensible para el operador.
- Archivos: `apps/tournament/views.py`.
- Solución: validar pertenencia dentro de la competencia y devolver JSON estructurado con HTTP 400.
- Estado: corregido y probado.

## H-13 — Recomendación de avance después del cierre

- Severidad: baja.
- Escenario: guardar el podio y volver al resumen o a la final.
- Resultado previo: el estado mostraba `Completado`, pero la interfaz seguía ofreciendo “Pasar a la siguiente fase” y una advertencia de participantes vivos.
- Causa raíz: `recommendation_ready` solo comprobaba si la fase estaba cerrada.
- Riesgo: confusión operativa al final del evento.
- Archivos: `apps/tournament/views.py`, plantillas `control_division.html` y `control_stage.html`.
- Solución: mostrar “Torneo completado / Torneo finalizado” y ocultar la acción de avance.
- Estado: corregido y probado.

## H-14 — Configuración de despliegue no endurecida

- Severidad: media, pendiente operativa.
- Escenario: `python manage.py check --deploy`.
- Resultado: seis advertencias: HSTS sin configurar, ausencia de redirección HTTPS, clave secreta débil, cookies de sesión/CSRF no seguras y `DEBUG=True`.
- Riesgo: exposición de sesiones, CSRF o información sensible si el servidor se publica en una red no confiable.
- Archivos: configuración y variables de entorno de despliegue.
- Solución propuesta: usar una clave aleatoria robusta, `DEBUG=False`, HTTPS, cookies seguras y configurar HSTS solo después de validar HTTPS.
- Estado: pendiente; no se cambió automáticamente para no romper el entorno local del evento.

## H-15 — Suite nativa PostgreSQL no ejecutable con el usuario actual

- Severidad: media, limitación de validación.
- Escenario: ejecutar `manage.py test` con la configuración PostgreSQL real.
- Resultado: Django intentó crear `test_robot_tournament` y PostgreSQL respondió “permission denied to create database”.
- Riesgo: los bloqueos `select_for_update()` fueron revisados y ejercitados lógicamente, pero no sometidos a una prueba concurrente real en PostgreSQL.
- Solución propuesta: crear una base de prueba separada o conceder temporalmente `CREATEDB` a un usuario exclusivo de CI/pruebas.
- Estado: pendiente operativa. No se usó la base real para evitar daños.

## H-16 — Coexistencia de motor progresivo y heredado

- Severidad: mejora futura.
- Escenario: Colegios nuevos usan flujo progresivo; la competencia real de Universidades conserva una configuración heredada con batallas precreadas.
- Riesgo: mayor superficie de mantenimiento y diferencias operativas entre categorías.
- Solución: mantener compatibilidad durante este evento; migrar solo en una edición futura y con respaldo/ensayo dedicado.
- Estado: ambos motores fueron simulados con 0, 1 y 2 repechajes; no se recomienda migrar la competencia real antes del torneo.
