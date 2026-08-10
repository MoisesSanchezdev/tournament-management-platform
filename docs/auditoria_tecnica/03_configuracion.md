# 03. Configuracion

## Archivo principal

Fuente: `config/settings.py`

## Carga de entorno

`config/settings.py` calcula `BASE_DIR` y carga `BASE_DIR / ".env"` con `load_dotenv`.

Funciones auxiliares confirmadas:

| Funcion | Uso |
| --- | --- |
| `env_bool(name, default=False)` | Convierte variables tipo booleano |
| `env_list(name, default="")` | Convierte listas separadas por coma |

## Variables de entorno documentadas

Fuente: `.env.example`

| Variable | Uso confirmado |
| --- | --- |
| `DJANGO_SECRET_KEY` | Clave secreta Django |
| `DJANGO_DEBUG` | Modo debug |
| `DJANGO_ALLOWED_HOSTS` | Hosts permitidos |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | Origenes confiables CSRF |
| `DJANGO_DATABASE` | Seleccion de SQLite local |
| `POSTGRES_DB` | Nombre base PostgreSQL |
| `POSTGRES_USER` | Usuario PostgreSQL |
| `POSTGRES_PASSWORD` | Password PostgreSQL |
| `POSTGRES_HOST` | Host PostgreSQL |
| `POSTGRES_PORT` | Puerto PostgreSQL |
| `DJANGO_EMAIL_BACKEND` | Backend de correo preferente |
| `EMAIL_BACKEND` | Backend alternativo soportado |
| `EMAIL_HOST` | Host SMTP |
| `EMAIL_PORT` | Puerto SMTP |
| `EMAIL_HOST_USER` | Usuario SMTP |
| `EMAIL_HOST_PASSWORD` | Password SMTP |
| `EMAIL_USE_TLS` | TLS SMTP |
| `EMAIL_USE_SSL` | SSL SMTP |
| `DEFAULT_FROM_EMAIL` | Remitente |
| `LIBREOFFICE_BINARY` | Ruta del binario LibreOffice |

## Apps instaladas

| Tipo | Apps |
| --- | --- |
| Django core | `admin`, `auth`, `contenttypes`, `sessions`, `messages`, `staticfiles` |
| Locales | `apps.core`, `apps.common`, `apps.participants`, `apps.tournament`, `apps.invitations.apps.InvitationsConfig` |

## Middleware

| Middleware | Proposito |
| --- | --- |
| `SecurityMiddleware` | Seguridad HTTP base |
| `SessionMiddleware` | Sesiones |
| `CommonMiddleware` | Utilidades HTTP comunes |
| `CsrfViewMiddleware` | Proteccion CSRF |
| `AuthenticationMiddleware` | Usuario autenticado |
| `MessageMiddleware` | Mensajes |
| `XFrameOptionsMiddleware` | Proteccion clickjacking |

## Base de datos

Reglas confirmadas:

1. `USE_SQLITE` es verdadero si `DJANGO_DATABASE=sqlite`.
2. Tambien es verdadero con `DEBUG=True`, sin `DJANGO_DATABASE` y sin `POSTGRES_DB`.
3. Si `USE_SQLITE=True` y `DEBUG=False`, se lanza `ImproperlyConfigured`.
4. Si no se usa SQLite, se exigen `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`.

## Archivos estaticos y media

| Setting | Valor |
| --- | --- |
| `STATIC_URL` | `static/` |
| `STATICFILES_DIRS` | `BASE_DIR / "static"` |
| `STATIC_ROOT` | `BASE_DIR / "staticfiles"` |
| `MEDIA_URL` | `media/` |
| `MEDIA_ROOT` | `BASE_DIR / "media"` |

## Seguridad por entorno

| Setting | Comportamiento |
| --- | --- |
| `DEBUG` | `False` por defecto |
| `SECRET_KEY` | Obligatoria cuando `DEBUG=False` |
| `ALLOWED_HOSTS` | Obligatorio cuando `DEBUG=False` |
| `CSRF_COOKIE_SECURE` | `not DEBUG` |
| `SESSION_COOKIE_SECURE` | `not DEBUG` |
| `SECURE_SSL_REDIRECT` | Solo cuando `not DEBUG` |
| `SECURE_HSTS_SECONDS` | `31536000` cuando `not DEBUG` |

## Configuracion no confirmada

| Punto | Estado |
| --- | --- |
| Valores reales de `.env` | Revisados solo como nombres de variables; valores no divulgados |
| Dominio final de produccion | NO CONFIRMADO |
| Configuracion de proxy/reverse proxy | NO CONFIRMADO |
| Almacenamiento externo de media | NO CONFIRMADO |
