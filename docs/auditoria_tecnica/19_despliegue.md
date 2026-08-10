# 19. Despliegue

## Configuracion preparada

| Area | Evidencia |
| --- | --- |
| WSGI | `config/wsgi.py` |
| ASGI | `config/asgi.py` |
| PostgreSQL | `config/settings.py` y `requirements.txt` |
| Static root | `STATIC_ROOT = BASE_DIR / "staticfiles"` |
| Media root | `MEDIA_ROOT = BASE_DIR / "media"` |
| Seguridad prod | Bloques `if not DEBUG` |
| Variables ejemplo | `.env.example` |

## Requisitos de entorno

| Requisito | Estado |
| --- | --- |
| Python | Version exacta no confirmada |
| Dependencias pip | `requirements.txt` |
| Base de datos | PostgreSQL para no-local |
| SMTP | Requerido para envio real |
| LibreOffice | Requerido para PDF de invitaciones |
| Servidor web/app | NO CONFIRMADO |

## Pasos tecnicos soportados por archivos

1. Crear entorno virtual.
2. Instalar `pip install -r requirements.txt`.
3. Configurar `.env` real.
4. Configurar PostgreSQL.
5. Ejecutar migraciones.
6. Crear superusuario.
7. Recolectar estaticos.
8. Levantar WSGI/ASGI.

## Comandos mencionados en README

| Comando | Uso |
| --- | --- |
| `python manage.py makemigrations` | Crear migraciones |
| `python manage.py migrate` | Aplicar migraciones |
| `python manage.py createsuperuser` | Crear admin |
| `python manage.py runserver` | Desarrollo local |
| `python manage.py check --deploy` | Verificacion despliegue |

Durante la auditoria no se ejecutaron comandos de migracion, collectstatic, commits ni push.

## Comunicaciones en despliegue

Para envio real deben existir `DJANGO_EMAIL_BACKEND`, `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `DEFAULT_FROM_EMAIL` y confirmacion explicita.

Para PDF debe existir LibreOffice en PATH o `LIBREOFFICE_BINARY`.

## No confirmado

| Punto | Estado |
| --- | --- |
| Hosting final | NO CONFIRMADO |
| Dominio final | NO CONFIRMADO |
| HTTPS/certificados | NO CONFIRMADO |
| Servicio de static files | NO CONFIRMADO |
| Servicio de media files | NO CONFIRMADO |
| Variables reales de produccion | NO CONFIRMADO |
| CI/CD | NO CONFIRMADO |
| Backups | NO CONFIRMADO |

## Riesgos de despliegue

1. Si `DEBUG=False` y faltan variables, Django no inicia.
2. Si LibreOffice no esta disponible, las invitaciones PDF fallan.
3. Si static files no se sirven correctamente, el panel pierde estilos y JS.
4. Si SMTP no esta validado, el modulo bloquea envios reales.
