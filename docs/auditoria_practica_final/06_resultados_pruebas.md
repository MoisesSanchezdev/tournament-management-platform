# 06. Resultados de pruebas

## Resumen

| Verificación | Resultado |
| --- | --- |
| Suite Django aislada | 46/46 exitosas |
| Pruebas prácticas nuevas del torneo | 34 |
| `manage.py check` | 0 incidencias |
| Migraciones pendientes | Ninguna |
| Dependencias rotas | Ninguna |
| Servidor temporal | HTTP 200 |
| Consola de navegador | 0 errores / 0 advertencias |
| Integridad de datos reales | 0 infracciones en 10 consultas |
| Prueba nativa PostgreSQL | No ejecutada: usuario sin permiso para crear base de test |
| Cobertura instrumental | No medida; no se añadió una dependencia de cobertura |

## Comandos principales

### Estado y entorno

```powershell
git status --short --branch
git log -1 --oneline
.\.venv\Scripts\python.exe --version
.\.venv\Scripts\python.exe -m django --version
.\.venv\Scripts\python.exe -m pip check
```

Resultado: rama y commit esperados, Python 3.12.10, Django 5.2.16 y dependencias consistentes.

### Checks de Django

```powershell
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
```

Resultado:

- `System check identified no issues (0 silenced).`
- `No changes detected`.

### Suite completa aislada

```powershell
$env:DJANGO_SETTINGS_MODULE='config.audit_settings'
$env:AUDIT_DATABASE_PATH='C:\Projects\pre_explotaglobos_audit_backups\20260727_195743\audit_test.sqlite3'
.\.venv\Scripts\python.exe manage.py test --verbosity 1
```

Resultado final:

```text
Found 46 test(s).
..............................................
Ran 46 tests in 22.601s
OK
```

La base de test fue SQLite en memoria y Django la destruyó al terminar.

## Cobertura funcional relevante

### Grupos y categorías

- Matriz automática para 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 16, 17, 24, 31, 32, 33, 40 y 73 participantes.
- Cada cantidad se probó en Colegios y Universidades.
- Reparto balanceado, sin faltantes, duplicados, mezcla de categorías ni grupos unitarios evitables.
- Reinicializar con resultados existentes no los borra silenciosamente.

### Flujo integral

- Colegio impar sin repechaje.
- Universidad con cuadro inicial exacto.
- Ambas categorías simultáneas.
- Motor progresivo y motor heredado.
- 0, 1 y 2 repechajes.
- Excedentes 17 y 33.
- Final, tercer lugar y podio de tres equipos únicos.

### Correcciones

- Corrección tardía de grupo.
- Corrección de clasificadores múltiples.
- Corrección de semifinal.
- Corrección después de guardar el podio.
- Corrección profunda que conserva un resultado paralelo no relacionado.
- Repetición idempotente de resultados.
- Segunda pestaña obsoleta bloqueada con 409.

### AJAX y seguridad

- Payload vacío: HTTP 400 con JSON.
- Grupo de otra competencia: HTTP 400 con JSON.
- Corrección sin confirmar: HTTP 409.
- Petición sin CSRF: HTTP 403.
- Ruta de movimiento manual retirada: HTTP 404.
- Reinicio de demo bloqueado sin setting o bandera.

## Prueba visual integral

Entorno temporal:

`C:\Projects\pre_explotaglobos_audit_backups\20260727_195743\ui_runtime_final_20260727_2030`

Datos:

- SQLite `audit_ui.sqlite3`.
- 8 equipos de Colegio y 8 de Universidad.
- Usuario organizador temporal.
- Servidor limitado a `127.0.0.1`.

Acciones validadas:

1. Inicio de sesión y panel.
2. Selección de clasificados en dos grupos.
3. Guardado individual y general.
4. Doble clic y confirmación única.
5. Recarga y persistencia de radios, clases de ganador/perdedor y conteos.
6. Creación de semifinal.
7. Guardado de ganadores.
8. Intento de corrección cancelado.
9. Corrección confirmada con sustitución del ganador.
10. Creación de final y tercer lugar.
11. Guardado del bronce y campeón.
12. Podio inferido y guardado.
13. Estado final `Completado`.
14. Universidad permaneció independiente en `Borrador`, con selecciones 0/2.
15. Modal de participante informativo, sin edición arbitraria.
16. Consola sin errores ni advertencias.

Después de la validación se cerraron las pestañas y se detuvo únicamente el servidor temporal de auditoría. La base temporal se conservó como evidencia.

## Arranque del servidor

Se inició el servidor de desarrollo con la configuración aislada y se consultó:

`http://127.0.0.1:8768/torneo/`

Resultado: HTTP 200, 2.751 bytes. Los procesos temporales asociados al puerto 8768 fueron identificados y detenidos al terminar.

## Base real: validación de solo lectura

La consulta se ejecutó con:

```sql
SET TRANSACTION READ ONLY;
```

Resultados:

| Regla | Infracciones |
| --- | ---: |
| Equipo en varios grupos de la misma competencia | 0 |
| Equipo repetido en una misma fase | 0 |
| Equipo duplicado en la misma batalla | 0 |
| Ganador ajeno a la batalla | 0 |
| Batalla finalizada sin ganador | 0 |
| Estado apuntando a grupo de otra competencia | 0 |
| Estado apuntando a batalla de otra competencia | 0 |
| Equipo presente en ambas divisiones | 0 |
| Final con más de dos entradas | 0 |
| Podio duplicado o incompleto | 0 |

## Pruebas fallidas y limitaciones

### Base de test PostgreSQL

Se intentó ejecutar las pruebas con la configuración PostgreSQL. Django confirmó que la base productiva era `robot_tournament` y que usaría `test_robot_tournament`, pero falló antes de ejecutar pruebas:

```text
permission denied to create database
```

No se elevó el permiso ni se reutilizó la base real. Esto preservó la regla de no hacer pruebas destructivas en producción.

### Check de despliegue

```powershell
.\.venv\Scripts\python.exe manage.py check --deploy
```

Resultado: 6 advertencias de seguridad:

- `security.W004`: HSTS sin configurar.
- `security.W008`: redirección HTTPS desactivada.
- `security.W009`: clave secreta débil.
- `security.W012`: cookie de sesión no segura.
- `security.W016`: cookie CSRF no segura.
- `security.W018`: `DEBUG=True`.

Estas advertencias no afectan la simulación local, pero deben resolverse antes de exponer el sistema públicamente.

### Git

`git diff --check` no encontró errores de espacios. Git emitió avisos de que en Windows podría convertir LF a CRLF la próxima vez que toque varios archivos; no es un fallo funcional.
