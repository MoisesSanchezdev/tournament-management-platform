# 05. Funciones retiradas o desactivadas

## Movimiento manual arbitrario de participantes

### Función retirada

El modal de participante permitía:

- mover a otra fase;
- mover a otro grupo;
- asignar una batalla;
- imponer un estado manual;
- guardar una nota junto con esos cambios.

También existía el endpoint:

`/torneo/control/divisiones/<competition_id>/participantes/<state_id>/actualizar/`

### Motivo técnico

La acción modificaba `TeamCompetitionState`, pero no garantizaba simultáneamente:

- reemplazo del participante en `DivisionGroupEntry` o `CompetitionBattleEntry`;
- retiro del participante anterior;
- recálculo de ganadores y clasificados;
- invalidación de batallas posteriores;
- actualización de semifinal, final y podio;
- prevención de un mismo equipo en posiciones incompatibles;
- preservación de resultados paralelos.

Por tanto, podía producir un estado visible que no coincidiera con la llave real. Repararla habría requerido duplicar el motor completo de correcciones y aumentaba el riesgo antes del evento.

### Alcance de la retirada

- Se retiró `participant_modal_update` de las vistas.
- Se eliminó su import y su ruta.
- Se eliminaron del JavaScript el formulario, los selectores y el envío AJAX.
- El modal conserva datos de participante, institución, fase, estado e historial.
- No se eliminaron modelos, estados ni entradas históricas.
- Las correcciones legítimas siguen disponibles mediante los resultados de grupo o batalla con confirmación y `manual_override`.

### Verificación

- La ruta anterior responde 404.
- No quedan botones ni formularios de movimiento en el modal.
- La tarjeta del participante continúa abriendo información e historial.
- La validación visual confirmó que el modal es de solo lectura.

## Comando destructivo de demostración

### Función desactivada por defecto

`reset_tournament_demo` no fue eliminado porque es útil para demostraciones y pruebas aisladas. Quedó bloqueado salvo que se cumplan simultáneamente:

1. `ALLOW_DESTRUCTIVE_DEMO_RESET=True` en una configuración explícitamente aislada.
2. Uso de `--confirm-demo-reset` en la línea de comandos.

Si falta cualquiera de las dos condiciones, el comando lanza `CommandError` antes de ejecutar eliminaciones.

### Verificación

- Configuración normal: bloqueado.
- Configuración aislada sin bandera CLI: bloqueado.
- Configuración aislada con confirmación: funciona sobre la base temporal.

## Funciones peligrosas que se conservaron

### Reiniciar torneo desde la interfaz

Se mantuvo porque puede ser una acción operativa legítima antes del inicio. Conserva:

- acceso restringido a organizadores;
- confirmación explícita del navegador;
- campo `confirm_reset=yes`;
- mensaje que advierte que se eliminará el progreso operativo.

Recomendación: no usarla una vez iniciado el torneo salvo que exista respaldo reciente y autorización del director del evento.

### Correcciones manuales de resultados

Se conservaron porque son necesarias ante errores humanos. Ahora:

- una repetición idéntica es idempotente;
- un cambio exige confirmación;
- una corrección tardía limpia dependencias incompatibles;
- los resultados paralelos no afectados se preservan;
- la interfaz y el backend comparten el contrato HTTP 409.

## Documentación principal

No se reescribieron manuales, PDF, LaTeX ni entregables. La sección del manual que describa el movimiento manual de participantes debe retirarse o aclarar que el modal es únicamente informativo. El comando de demostración debe documentar las dos barreras obligatorias.
