# 02. Tecnologias

## Dependencias Python

Fuente: `requirements.txt`

| Dependencia | Version declarada | Uso confirmado |
| --- | --- | --- |
| `Django` | `>=5.2,<5.3` | Framework web, ORM, templates, auth, admin, comandos |
| `psycopg[binary]` | `>=3.2,<3.3` | Driver PostgreSQL |
| `python-dotenv` | `>=1.0,<2.0` | Carga de `.env` en `config/settings.py` |
| `openpyxl` | `>=3.1,<3.2` | Lectura de destinatarios XLSX en `apps/invitations/services.py` |
| `python-docx` | `>=1.1,<1.2` | Lectura/render de plantillas DOCX en `apps/invitations/services.py` |

## Stack confirmado

| Capa | Tecnologia |
| --- | --- |
| Backend | Python + Django |
| ORM | Django ORM |
| Base de datos desarrollo | SQLite cuando `DJANGO_DATABASE=sqlite` y `DJANGO_DEBUG=True` |
| Base de datos no local | PostgreSQL mediante variables `POSTGRES_*` |
| Frontend | Django Templates, HTML, CSS, JavaScript |
| Assets | `static/` para CSS, JS, PDF y logos |
| Comunicaciones | `django.core.mail`, SMTP o consola |
| Documentos | DOCX con `python-docx`, PDF con LibreOffice headless |
| Excel | XLSX con `openpyxl` |

## Runtime validado

| Elemento | Resultado |
| --- | --- |
| Python de `.venv` | `C:\Projects\pre_explotaglobos\.venv\Scripts\python.exe` |
| Comando ejecutado | `.venv\Scripts\python.exe manage.py check` |
| Resultado | `System check identified no issues (0 silenced).` |

## Tecnologias no confirmadas

| Elemento | Estado |
| --- | --- |
| Servidor WSGI/ASGI de produccion | NO CONFIRMADO |
| Proveedor de hosting | NO CONFIRMADO |
| Version exacta de Python usada en produccion | NO CONFIRMADO |
| Servicio SMTP real | NO CONFIRMADO; solo se confirma soporte por configuracion |
| Binario LibreOffice instalado en entorno final | NO CONFIRMADO |

## Dependencias externas por modulo

| Modulo | Dependencia externa |
| --- | --- |
| `apps/invitations/services.py` | LibreOffice via `subprocess.run` para DOCX a PDF |
| `apps/invitations/services.py` | SMTP real si `EMAIL_BACKEND` es `django.core.mail.backends.smtp.EmailBackend` |
| `apps/core/views.py` | URLs externas de imagenes y sitios de patrocinadores |

## Riesgos tecnologicos

1. La conversion PDF depende de que LibreOffice exista en PATH o `LIBREOFFICE_BINARY`.
2. No se confirma configuracion de servidor de archivos estaticos en produccion.
3. El uso de SQLite esta bloqueado fuera de debug, pero debe validarse que produccion suministre todas las variables PostgreSQL.
