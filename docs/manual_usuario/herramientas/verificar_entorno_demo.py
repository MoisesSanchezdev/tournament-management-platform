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
from django.contrib.auth import get_user_model  # noqa: E402
from django.db import connection  # noqa: E402


def main() -> None:
    django.setup()
    from apps.participants.models import SchoolRegistration, Team, UniversityRegistration  # noqa: E402
    from apps.tournament.models import DivisionCompetition, TournamentEdition  # noqa: E402
    from apps.invitations.models import CommunicationBatch, CommunicationLog, CommunicationRecipient, CommunicationTemplate  # noqa: E402

    db_path = Path(connection.settings_dict["NAME"]).resolve()
    demo_root = settings.DEMO_ROOT.resolve()
    official_db = (settings.BASE_DIR / "db.sqlite3").resolve()
    checks = {
        "settings_module": os.environ["DJANGO_SETTINGS_MODULE"],
        "database_path": str(db_path),
        "database_exists": db_path.exists(),
        "database_inside_demo": demo_root in db_path.parents,
        "not_official_database": db_path != official_db,
        "email_backend": settings.EMAIL_BACKEND,
        "email_safe": settings.EMAIL_BACKEND != "django.core.mail.backends.smtp.EmailBackend",
        "email_file_path": str(getattr(settings, "EMAIL_FILE_PATH", "")),
        "media_root": str(settings.MEDIA_ROOT),
        "smtp_host": getattr(settings, "EMAIL_HOST", ""),
        "users": get_user_model().objects.count(),
        "editions": TournamentEdition.objects.count(),
        "teams": Team.objects.count(),
        "school_registrations": SchoolRegistration.objects.count(),
        "university_registrations": UniversityRegistration.objects.count(),
        "competitions": DivisionCompetition.objects.count(),
        "communication_templates": CommunicationTemplate.objects.count(),
        "communication_recipients": CommunicationRecipient.objects.count(),
        "communication_batches": CommunicationBatch.objects.count(),
        "communication_logs": CommunicationLog.objects.count(),
    }
    if not checks["database_inside_demo"] or not checks["not_official_database"] or not checks["email_safe"]:
        raise SystemExit(json.dumps(checks, indent=2))
    print(json.dumps(checks, indent=2))


if __name__ == "__main__":
    main()
