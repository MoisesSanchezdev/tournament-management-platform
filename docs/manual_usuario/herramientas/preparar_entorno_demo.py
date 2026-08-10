import json
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "docs.manual_usuario.herramientas.demo_settings")

import django  # noqa: E402
from django.conf import settings  # noqa: E402


def assert_inside_demo(path: Path) -> None:
    resolved = path.resolve()
    demo_root = settings.DEMO_ROOT.resolve()
    if demo_root not in resolved.parents and resolved != demo_root:
        raise SystemExit(f"Ruta fuera del entorno demo: {resolved}")


def main() -> None:
    django.setup()
    for directory in [settings.DEMO_ROOT, settings.DEMO_DATA_DIR, settings.DEMO_MEDIA_ROOT, settings.DEMO_MAIL_PATH]:
        assert_inside_demo(Path(directory))
        Path(directory).mkdir(parents=True, exist_ok=True)

    credentials = {
        "username": "operador_documentacion",
        "password": "DemoManualUsuario2026!",
        "email": "operador@example.com",
        "note": "Credenciales ficticias exclusivas de la base temporal demo. No incluir en entregables finales.",
    }
    credentials_path = settings.DEMO_ROOT / "credenciales_demo.local.json"
    assert_inside_demo(credentials_path)
    credentials_path.write_text(json.dumps(credentials, indent=2), encoding="utf-8")

    evidence = {
        "settings_module": os.environ["DJANGO_SETTINGS_MODULE"],
        "database_engine": settings.DATABASES["default"]["ENGINE"],
        "database_name": str(settings.DATABASES["default"]["NAME"]),
        "official_database_name": str(settings.BASE_DIR / "db.sqlite3"),
        "database_inside_demo": str(settings.DEMO_ROOT.resolve()) in str(Path(settings.DATABASES["default"]["NAME"]).resolve()),
        "email_backend": settings.EMAIL_BACKEND,
        "email_file_path": str(settings.EMAIL_FILE_PATH),
        "media_root": str(settings.MEDIA_ROOT),
        "allowed_hosts": settings.ALLOWED_HOSTS,
        "debug": settings.DEBUG,
        "migrate_command": "C:\\Projects\\pre_explotaglobos\\.venv\\Scripts\\python.exe manage.py migrate --settings=docs.manual_usuario.herramientas.demo_settings",
    }
    evidence_path = settings.DEMO_ROOT / "evidencia_entorno_demo.json"
    evidence_path.write_text(json.dumps(evidence, indent=2), encoding="utf-8")
    print(json.dumps(evidence, indent=2))


if __name__ == "__main__":
    main()
