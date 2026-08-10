from config.settings import *  # noqa: F403,F401

DEMO_ROOT = BASE_DIR / "docs" / "manual_usuario" / "entorno_demo"  # noqa: F405
DEMO_DATA_DIR = DEMO_ROOT / "datos"
DEMO_DB_PATH = DEMO_DATA_DIR / "db_demo.sqlite3"
DEMO_MEDIA_ROOT = DEMO_ROOT / "media"
DEMO_MAIL_PATH = DEMO_ROOT / "mail_outbox"

DEBUG = True
SECRET_KEY = "manual-usuario-demo-insecure-key"
ALLOWED_HOSTS = ["127.0.0.1", "localhost", "testserver"]
CSRF_TRUSTED_ORIGINS = ["http://127.0.0.1:8765", "http://localhost:8765"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": DEMO_DB_PATH,
    }
}

ALLOW_DESTRUCTIVE_DEMO_RESET = True

MEDIA_ROOT = DEMO_MEDIA_ROOT
MEDIA_URL = "/media/"
STATIC_ROOT = DEMO_ROOT / "staticfiles"

EMAIL_BACKEND = "django.core.mail.backends.filebased.EmailBackend"
EMAIL_FILE_PATH = DEMO_MAIL_PATH
EMAIL_HOST = ""
EMAIL_PORT = 25
EMAIL_HOST_USER = ""
EMAIL_HOST_PASSWORD = ""
EMAIL_USE_TLS = False
EMAIL_USE_SSL = False
DEFAULT_FROM_EMAIL = "documentacion@example.com"
SERVER_EMAIL = DEFAULT_FROM_EMAIL
LIBREOFFICE_BINARY = ""

CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = False
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False

PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
