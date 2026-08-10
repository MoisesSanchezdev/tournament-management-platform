# Diseno del entorno demo

## Principio de aislamiento

El entorno demo usa una configuracion temporal, localizada dentro de `docs/manual_usuario/`, sin modificar `config/settings.py`, `.env`, dependencias ni codigo funcional.

Settings usado:

```text
docs.manual_usuario.herramientas.demo_settings
```

Este settings importa la configuracion real y reemplaza solo valores necesarios para documentacion visual:

| Aspecto | Valor demo |
| --- | --- |
| Base de datos | SQLite temporal en `docs/manual_usuario/entorno_demo/datos/db_demo.sqlite3` |
| Correo | `django.core.mail.backends.filebased.EmailBackend` |
| Outbox | `docs/manual_usuario/entorno_demo/mail_outbox` |
| Media | `docs/manual_usuario/entorno_demo/media` |
| DEBUG | `True` solo para proceso demo |
| Hosts | `127.0.0.1`, `localhost`, `testserver` |
| SMTP | Desactivado: host, usuario y password vacios |
| Secret key | Ficticia, exclusiva del proceso demo |

## Comandos documentados

Preparacion previa a migracion:

```powershell
& C:\Projects\pre_explotaglobos\.venv\Scripts\python.exe docs\manual_usuario\herramientas\preparar_entorno_demo.py
```

Migracion temporal autorizada:

```powershell
& C:\Projects\pre_explotaglobos\.venv\Scripts\python.exe manage.py migrate --settings=docs.manual_usuario.herramientas.demo_settings --noinput
```

Poblamiento ficticio:

```powershell
& C:\Projects\pre_explotaglobos\.venv\Scripts\python.exe docs\manual_usuario\herramientas\poblar_datos_demo.py
```

Verificacion:

```powershell
& C:\Projects\pre_explotaglobos\.venv\Scripts\python.exe docs\manual_usuario\herramientas\verificar_entorno_demo.py
```

## Evidencia previa a migracion

El script de preparacion registro:

- base temporal: `C:\Projects\pre_explotaglobos\docs\manual_usuario\entorno_demo\datos\db_demo.sqlite3`;
- base oficial: `C:\Projects\pre_explotaglobos\db.sqlite3`;
- `database_inside_demo=true`;
- backend de correo file-based;
- media root dentro de `entorno_demo`;
- comando de migracion exacto.

## Datos ficticios creados

| Tipo de dato | Cantidad |
| --- | ---: |
| Usuario admin temporal | 1 |
| Edicion demo | 1 |
| Reglas demo | 3 |
| Equipos demo | 10 |
| Registros escolares submitted | 2 |
| Registro universitario submitted | 1 |
| Competencias por division | 2 |
| Plantilla de comunicacion demo | 1 |
| Destinatarios demo | 3 |
| Lote de comunicacion simulado | 1 |
| Log de comunicacion dry-run | 1 |

Las credenciales ficticias quedaron en `docs/manual_usuario/entorno_demo/credenciales_demo.local.json`, archivo ignorado por `.gitignore` local del entorno demo.

## Politica de privacidad

Todos los correos usan `example.com`. Los nombres visibles son ficticios: Equipo Andromeda, Equipo Vector, Equipo Kilobyte, Institucion Demo Norte, Universidad de Ejemplo y equivalentes. No se copiaron participantes reales ni datos de la base oficial.
