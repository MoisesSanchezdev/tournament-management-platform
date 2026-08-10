import tempfile
from itertools import product
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction

from apps.participants.forms import normalize_robot_name
from apps.participants.models import (
    Institution,
    InstitutionType,
    RegistrationStatus,
    SchoolParticipant,
    SchoolRegistration,
    Team,
    TeamMember,
    UniversityParticipant,
    UniversityRegistration,
)
from apps.tournament.models import (
    CompetitionBattle,
    CompetitionBattleEntry,
    DivisionCompetition,
    DivisionGroup,
    DivisionGroupEntry,
    Match,
    RuleSection,
    TournamentEdition,
    TournamentPhase,
)
from apps.tournament.services import initialize_competition


SCHOOL_INSTITUTIONS = [
    "Institucion Educativa Tecnica Ciudad de Pereira",
    "Colegio Bilingue del Cafe",
    "Liceo Campestre Futuro",
    "Colegio Industrial Risaralda",
    "Institucion Educativa Santa Isabel",
    "Colegio Cientifico San Nicolas",
    "Instituto Tecnologico del Otun",
    "Colegio Metropolitano de Dosquebradas",
    "Liceo Innovacion Andina",
    "Institucion Educativa Villa Olimpica",
]

UNIVERSITY_INSTITUTIONS = [
    "Universidad Tecnologica de Pereira",
    "Universidad Nacional de Colombia",
    "Universidad de Caldas",
    "Universidad del Quindio",
    "Universidad de Antioquia",
    "Universidad del Valle",
    "Universidad Industrial de Santander",
    "Universidad EAFIT",
    "Pontificia Universidad Javeriana",
    "Universidad de los Andes",
]

RESPONSIBLE_NAMES = [
    "Carlos Andres Mejia",
    "Liliana Marcela Rios",
    "Juan David Restrepo",
    "Sandra Milena Arango",
    "Diego Fernando Cardona",
    "Paula Andrea Henao",
    "Sergio Alexander Ocampo",
    "Monica Patricia Gil",
    "Luis Fernando Castaño",
    "Adriana Marcela Jaramillo",
]

FIRST_NAMES = [
    "Santiago",
    "Valentina",
    "Juan",
    "Salome",
    "Mateo",
    "Isabella",
    "Samuel",
    "Mariana",
    "Nicolas",
    "Gabriela",
    "Sebastian",
    "Luciana",
    "Daniel",
    "Emilia",
    "Martin",
    "Sara",
    "Tomas",
    "Antonella",
    "Emmanuel",
    "Camila",
]

LAST_NAMES = [
    "Gomez",
    "Restrepo",
    "Lopez",
    "Henao",
    "Cardona",
    "Arango",
    "Mejia",
    "Rivera",
    "Ramirez",
    "Velez",
    "Castaño",
    "Giraldo",
    "Montoya",
    "Duque",
    "Herrera",
    "Marin",
    "Toro",
    "Quintero",
    "Rios",
    "Ospina",
]

ROBOT_PREFIXES = [
    "Aero",
    "Atlas",
    "Binary",
    "Centella",
    "Circuito",
    "Cosmos",
    "Cyclone",
    "Dynamo",
    "Electra",
    "Fusion",
    "Helix",
    "Ion",
    "Nebula",
    "Nova",
    "Plasma",
    "Quantum",
    "Razor",
    "Spark",
    "Turbo",
    "Vector",
    "Vertex",
    "Vortex",
]

ROBOT_SUFFIXES = [
    "Aurora",
    "Blade",
    "Boreal",
    "Drift",
    "Fenix",
    "Impulse",
    "Matrix",
    "Nitro",
    "Orbit",
    "Pulse",
    "Raptor",
    "Solar",
    "Spark",
    "Storm",
    "Strike",
    "Titan",
    "Turbo",
    "Ultra",
    "Volt",
    "Wave",
]


def build_robot_names(total: int) -> list[str]:
    names = []
    seen = set()
    for prefix, suffix in product(ROBOT_PREFIXES, ROBOT_SUFFIXES):
        candidate = f"{prefix} {suffix}"
        normalized = normalize_robot_name(candidate)
        if normalized in seen:
            continue
        names.append(candidate)
        seen.add(normalized)
        if len(names) == total:
            return names
    raise ValueError("No fue posible generar suficientes nombres de robot unicos para la simulacion.")


def participant_name(index: int) -> str:
    first_name = FIRST_NAMES[index % len(FIRST_NAMES)]
    last_name = LAST_NAMES[(index * 3) % len(LAST_NAMES)]
    return f"{first_name} {last_name}"


def create_registration_bundle(
    *,
    edition,
    division_label: str,
    index: int,
    robot_name: str,
    institution_name: str,
    responsible_name: str,
    registration_model,
    participant_model,
    institution_type: str,
    member_base_age: int,
):
    email = f"{division_label.lower()}_{index:03d}@simulacion.robot"
    phone = f"3{index:09d}"[-10:]
    registration = registration_model.objects.create(
        edition=edition,
        institution_name=institution_name,
        responsible_name=responsible_name,
        robot_name=robot_name,
        contact_phone=phone,
        contact_email=email,
        status=RegistrationStatus.APPROVED,
    )

    member_count = 1 if index % 5 == 0 else 2 if index % 2 == 0 else 3
    created_participants = []
    for offset in range(member_count):
        document_number = str(1000000000 + index * 10 + offset)
        participant = participant_model.objects.create(
            registration=registration,
            full_name=participant_name(index + offset),
            document_number=document_number,
            role="lider" if offset == 0 else f"integrante {offset + 1}",
            is_team_lead=offset == 0,
        )
        created_participants.append(participant)

    institution, _ = Institution.objects.get_or_create(
        name=institution_name,
        defaults={"institution_type": institution_type},
    )
    team = Team.objects.create(
        edition=edition,
        name=robot_name,
        institution=institution,
        category_label="Colegios" if institution_type == InstitutionType.SCHOOL else "Universidades",
        robot_name=robot_name,
        coach_name=responsible_name,
        coach_email=email,
        coach_phone=phone,
        status=RegistrationStatus.APPROVED,
        notes="Equipo generado automaticamente para simulacion del torneo.",
    )

    for offset, participant in enumerate(created_participants):
        TeamMember.objects.create(
            team=team,
            full_name=participant.full_name,
            document_number=participant.document_number,
            email=email if participant.is_team_lead else "",
            age=member_base_age + offset,
            role=participant.role,
            is_team_lead=participant.is_team_lead,
        )


class Command(BaseCommand):
    help = "Limpia los datos operativos y crea una simulacion completa con 50 colegios y 50 universidades."

    def add_arguments(self, parser):
        parser.add_argument("--school-count", type=int, default=50, help="Cantidad de registros de colegios.")
        parser.add_argument("--university-count", type=int, default=50, help="Cantidad de registros de universidades.")
        parser.add_argument(
            "--confirm-demo-reset",
            action="store_true",
            help="Confirma que se borrara unicamente una base temporal de demostracion.",
        )

    def handle(self, *args, **options):
        if not getattr(settings, "ALLOW_DESTRUCTIVE_DEMO_RESET", False):
            raise CommandError(
                "reset_tournament_demo esta deshabilitado en este entorno. "
                "Usa una configuracion temporal con ALLOW_DESTRUCTIVE_DEMO_RESET=True."
            )
        if not options["confirm_demo_reset"]:
            raise CommandError(
                "Debes agregar --confirm-demo-reset para confirmar el borrado de la base demo aislada."
            )

        database_name = str(connection.settings_dict.get("NAME") or "")
        is_memory_database = database_name == ":memory:" or database_name.startswith("file:memorydb_")
        if connection.vendor != "sqlite":
            raise CommandError("reset_tournament_demo solo puede ejecutarse sobre una base SQLite aislada.")
        if not is_memory_database:
            database_path = Path(database_name).resolve()
            allowed_roots = [Path(tempfile.gettempdir()).resolve()]
            demo_root = getattr(settings, "DEMO_ROOT", None)
            if demo_root:
                allowed_roots.append(Path(demo_root).resolve())
            if not any(
                root == database_path or root in database_path.parents
                for root in allowed_roots
            ):
                raise CommandError(
                    "La base demo debe estar en el directorio temporal del sistema o dentro de "
                    "DEMO_ROOT; no se elimino ningun dato."
                )
        school_count = options["school_count"]
        university_count = options["university_count"]
        if school_count < 0 or university_count < 0:
            raise ValueError("Las cantidades no pueden ser negativas.")

        with transaction.atomic():
            Match.objects.all().delete()
            TournamentPhase.objects.all().delete()
            CompetitionBattleEntry.objects.all().delete()
            CompetitionBattle.objects.all().delete()
            DivisionGroupEntry.objects.all().delete()
            DivisionGroup.objects.all().delete()
            DivisionCompetition.objects.all().delete()
            Team.objects.all().delete()
            Institution.objects.all().delete()
            SchoolRegistration.objects.all().delete()
            UniversityRegistration.objects.all().delete()
            RuleSection.objects.all().delete()
            TournamentEdition.objects.all().delete()

            edition = TournamentEdition.objects.create(
                name="Simulacion operativa Explota Globos 2026",
                description=(
                    f"Edicion de trabajo creada para simular {school_count} carros de colegio y {university_count} carros de universidad "
                    "con el formato actual del torneo."
                ),
                location="Universidad Tecnologica de Pereira",
                is_active=True,
            )

            rules = [
                (
                    "Reglamento oficial",
                    "La referencia oficial se consulta en el PDF embebido del sitio.",
                    "Esta edicion de simulacion conserva el reglamento publicado actualmente en la plataforma.",
                ),
                (
                    "Registro unico",
                    "Cada robot y cada participante deben ser exclusivos dentro de la edicion activa.",
                    "No se aceptan robots con nombres repetidos o variantes numeradas, ni documentos repetidos entre participantes.",
                ),
                (
                    "Modelo de fases",
                    "Se trabaja con grupos, purgatorios, octavos, cuartos, semifinales y final.",
                    "El panel interno ya queda listo para que el equipo organizador pruebe el flujo separado de colegios y universidades.",
                ),
            ]
            for order, (title, summary, body) in enumerate(rules, start=1):
                RuleSection.objects.create(
                    edition=edition,
                    title=title,
                    summary=summary,
                    body=body,
                    order=order,
                    is_published=True,
                )

            robot_names = build_robot_names(school_count + university_count)

            for index in range(school_count):
                create_registration_bundle(
                    edition=edition,
                    division_label="school",
                    index=index + 1,
                    robot_name=robot_names[index],
                    institution_name=SCHOOL_INSTITUTIONS[index % len(SCHOOL_INSTITUTIONS)],
                    responsible_name=RESPONSIBLE_NAMES[index % len(RESPONSIBLE_NAMES)],
                    registration_model=SchoolRegistration,
                    participant_model=SchoolParticipant,
                    institution_type=InstitutionType.SCHOOL,
                    member_base_age=14,
                )

            for index in range(university_count):
                create_registration_bundle(
                    edition=edition,
                    division_label="university",
                    index=index + school_count + 1,
                    robot_name=robot_names[index + school_count],
                    institution_name=UNIVERSITY_INSTITUTIONS[index % len(UNIVERSITY_INSTITUTIONS)],
                    responsible_name=RESPONSIBLE_NAMES[(index + 3) % len(RESPONSIBLE_NAMES)],
                    registration_model=UniversityRegistration,
                    participant_model=UniversityParticipant,
                    institution_type=InstitutionType.UNIVERSITY,
                    member_base_age=18,
                )

            school_competition = initialize_competition(edition, "school") if school_count >= 4 else None
            university_competition = initialize_competition(edition, "university") if university_count >= 4 else None

        self.stdout.write(self.style.SUCCESS("Base operativa reiniciada para simulacion."))
        self.stdout.write(
            self.style.SUCCESS(
                f"Se crearon {school_count} registros de colegio y {university_count} de universidad."
            )
        )
        self.stdout.write(self.style.SUCCESS(f"Edicion activa: {edition.name}"))
        if school_competition:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Colegios: {school_competition.configuration.get('label')} con {school_competition.groups.count()} grupos."
                )
            )
        if university_competition:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Universidades: {university_competition.configuration.get('label')} con {university_competition.groups.count()} grupos."
                )
            )
