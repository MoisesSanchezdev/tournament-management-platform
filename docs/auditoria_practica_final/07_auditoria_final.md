# 07. Auditoría final

## Dictamen

**APROBADO CON OBSERVACIONES**

**Calificación general: 91/100**

| Área | Puntaje |
| --- | ---: |
| Integridad y preservación de datos | 24/25 |
| Flujo funcional del torneo | 28/30 |
| Correcciones humanas y repechajes | 15/15 |
| Interfaz, AJAX y persistencia | 14/15 |
| Preparación de despliegue y operación | 10/15 |
| **Total** | **91/100** |

## Conclusión ejecutiva

El sistema puede completar torneos de Colegios y Universidades desde grupos hasta podio en los escenarios simulados. Las fallas críticas reproducidas —clasificados obsoletos después de correcciones, podio desactualizado y reutilización indebida en repechajes— fueron corregidas mediante cambios localizados y quedaron cubiertas por pruebas.

No quedan errores críticos conocidos. La base real no presenta infracciones en las consultas de integridad auditadas y no fue modificada por las simulaciones. La suite total de 46 pruebas pasa, Django no reporta incidencias y la interfaz aislada completó un torneo realista con persistencia tras recargas.

El dictamen no sube a “APROBADO PARA TORNEO” sin observaciones por dos razones operativas:

1. No fue posible ejecutar la suite sobre una base de test PostgreSQL porque el usuario no tiene permiso para crearla; falta una prueba concurrente nativa de los bloqueos.
2. La configuración de despliegue mantiene seis advertencias de seguridad que son aceptables solo para uso local/controlado, no para publicación abierta.

## Errores críticos pendientes

Ninguno conocido.

## Escenarios validados

- 2 y 3 participantes: detención segura, sin grupos o byes ficticios.
- 4 a 73 participantes, incluidos pares, impares e incómodos.
- Distribución balanceada en ambas categorías.
- Categorías operadas simultáneamente y sin mezcla.
- Motor progresivo y motor heredado.
- Torneos con cero, uno y dos repechajes.
- Cantidad impar, cuadro exacto y participantes excedentes.
- Correcciones antes y después de materializar fases.
- Corrección después de guardar final/podio.
- Doble petición, formulario vacío, ID cruzado, CSRF y dos pestañas.
- Recarga, navegación, clases visuales, mensajes y modales.
- Final, tercer lugar y podio único.
- Comando destructivo de demo bloqueado por defecto.
- Ruta de movimiento arbitrario retirada.

## Escenarios no validados completamente

- Dos transacciones PostgreSQL realmente concurrentes compitiendo por la misma fila.
- Restauración completa del respaldo PostgreSQL en otro servidor.
- Carga de muchos organizadores simultáneos o pruebas de rendimiento sostenido.
- Operación pública detrás de HTTPS/proxy con la configuración definitiva.
- Navegadores y dispositivos distintos del navegador de auditoría.
- Fallas físicas de red o energía durante una transacción.

## Riesgos residuales para el evento

### Medio — PostgreSQL sin prueba concurrente nativa

La solución usa `transaction.atomic()` y `select_for_update()` con un orden consistente. La lógica es correcta y las pruebas de pestaña obsoleta pasan, pero debe ensayarse en una base PostgreSQL de prueba.

### Medio — Configuración de seguridad de despliegue

No exponer el servidor actual directamente a Internet. Si la operación será por red, definir clave secreta robusta, `DEBUG=False`, hosts permitidos, HTTPS y cookies seguras.

### Bajo — Dos motores de competencia

La competencia real de Universidades usa el motor heredado; Colegios puede usar el progresivo. Ambos pasan las simulaciones. No migrar ni cambiar de motor durante el evento.

### Bajo — Acciones destructivas legítimas

“Reiniciar torneo” sigue disponible para organizadores con confirmación porque puede ser necesario antes de empezar. Durante la competencia debe tratarse como una acción excepcional y autorizada.

## Recomendaciones antes del día del torneo

1. Restaurar `robot_tournament.pgcustom` en un PostgreSQL separado y practicar el procedimiento de recuperación.
2. Crear un usuario/base PostgreSQL exclusiva de pruebas y ejecutar allí las 46 pruebas.
3. Resolver las seis advertencias de `check --deploy` si el sistema será accesible fuera del equipo local.
4. Hacer un respaldo PostgreSQL nuevo justo antes de abrir registros de resultados.
5. Congelar inscripciones y configuraciones de grupo antes del primer resultado.
6. Confirmar por escrito qué categoría usa el flujo progresivo y cuál conserva el heredado.
7. Asignar un operador principal por categoría; evitar que dos personas editen la misma batalla simultáneamente.
8. Ante una corrección tardía, leer la advertencia completa y verificar la fase posterior antes de confirmar.
9. No ejecutar `reset_tournament_demo` ni “Reiniciar torneo” durante el evento.
10. Mantener visible el registro de servidor y revisar cualquier HTTP 500 o 409 inesperado.

## Procedimiento operativo sugerido

### Antes de iniciar

- Ejecutar `manage.py check`.
- Verificar que la edición activa y los conteos de equipos coincidan con la lista oficial.
- Abrir Colegios y Universidades por separado y confirmar tamaños de grupos.
- Tomar respaldo y registrar su hash.

### Durante cada fase

- Guardar un grupo o batalla y verificar el mensaje de éxito.
- Recargar una vez antes de crear la siguiente fase.
- Comparar el número de vivos, clasificados y eliminados con la planilla oficial.
- Usar la recomendación del sistema; recurrir al modo manual solo si el formato ha sido aprobado.

### Si se registra un ganador incorrecto

- No mover al participante desde otra pantalla.
- Volver al resultado original.
- Seleccionar el resultado correcto.
- Revisar la advertencia de consecuencias.
- Confirmar `manual_override`.
- Verificar la primera fase dependiente y reconstruir los resultados invalidados.

### Al finalizar

- Completar el duelo de tercer lugar antes de cerrar el podio.
- Confirmar tres equipos únicos.
- Guardar el podio y comprobar que la categoría muestre `Completado` y `Torneo finalizado`.
- Tomar respaldo final.

## Evidencia

- Estado inicial: `01_estado_inicial.md`.
- Matriz: `02_matriz_simulaciones.md`.
- Hallazgos: `03_hallazgos.md`.
- Correcciones: `04_correcciones_realizadas.md`.
- Funciones retiradas: `05_funciones_retiradas_o_desactivadas.md`.
- Pruebas: `06_resultados_pruebas.md`.
