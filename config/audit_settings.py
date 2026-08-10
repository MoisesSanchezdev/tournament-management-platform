import os
from pathlib import Path

from .settings import *  # noqa: F401,F403


AUDIT_DATABASE_PATH = Path(os.environ["AUDIT_DATABASE_PATH"]).resolve()

DEBUG = True
SECRET_KEY = "audit-local-insecure-key"
ALLOWED_HOSTS = ["127.0.0.1", "localhost", "testserver"]
CSRF_TRUSTED_ORIGINS = ["http://127.0.0.1:8766", "http://localhost:8766"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": AUDIT_DATABASE_PATH,
    }
}

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False
SECURE_HSTS_SECONDS = 0
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
ALLOW_DESTRUCTIVE_DEMO_RESET = False
