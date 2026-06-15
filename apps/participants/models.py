import uuid

from django.core.validators import EmailValidator, RegexValidator
from django.db import models

from apps.common.models import TimeStampedModel


class InstitutionType(models.TextChoices):
    SCHOOL = "school", "Colegio"
    UNIVERSITY = "university", "Universidad"


class RegistrationStatus(models.TextChoices):
    DRAFT = "draft", "Borrador"
    SUBMITTED = "submitted", "Enviada"
    APPROVED = "approved", "Aprobada"
    REJECTED = "rejected", "Rechazada"


class RegistrationBase(TimeStampedModel):
    edition = models.ForeignKey(
        "tournament.TournamentEdition",
        on_delete=models.PROTECT,
        related_name="%(class)ss",
    )
    institution_name = models.CharField(max_length=180)
    responsible_name = models.CharField(max_length=120)
    robot_name = models.CharField(max_length=120)
    contact_phone = models.CharField(
        max_length=20,
        validators=[RegexValidator(r"^[0-9+\-\s]{7,20}$", "Ingresa un telefono valido.")],
    )
    contact_email = models.EmailField(validators=[EmailValidator()])
    status = models.CharField(
        max_length=20,
        choices=RegistrationStatus.choices,
        default=RegistrationStatus.SUBMITTED,
    )
    attendance_token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    receipt_email_sent_at = models.DateTimeField(null=True, blank=True)
    attendance_request_sent_at = models.DateTimeField(null=True, blank=True)
    attendance_confirmed_at = models.DateTimeField(null=True, blank=True)
    team_synced_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True
        ordering = ["-created_at"]


class SchoolRegistration(RegistrationBase):
    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["edition", "status"]),
            models.Index(fields=["institution_name"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["edition", "institution_name", "robot_name"],
                name="unique_school_robot_registration",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.robot_name} - {self.institution_name}"


class UniversityRegistration(RegistrationBase):
    semester = models.PositiveSmallIntegerField(
        default=1,
        help_text="Semestre actual del equipo universitario. Solo participan estudiantes hasta cuarto semestre.",
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["edition", "status"]),
            models.Index(fields=["institution_name"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["edition", "institution_name", "robot_name"],
                name="unique_university_robot_registration",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.robot_name} - {self.institution_name}"


class ParticipantBase(TimeStampedModel):
    full_name = models.CharField(max_length=120)
    document_number = models.CharField(max_length=30)
    role = models.CharField(max_length=80, blank=True, help_text="Ej: lider, integrante 2, integrante 3.")
    is_team_lead = models.BooleanField(default=False)

    class Meta:
        abstract = True
        ordering = ["full_name"]


class SchoolParticipant(ParticipantBase):
    registration = models.ForeignKey(
        SchoolRegistration,
        on_delete=models.CASCADE,
        related_name="participants",
    )

    class Meta:
        ordering = ["full_name"]
        indexes = [models.Index(fields=["document_number"])]

    def __str__(self) -> str:
        return f"{self.full_name} - {self.registration.robot_name}"


class UniversityParticipant(ParticipantBase):
    registration = models.ForeignKey(
        UniversityRegistration,
        on_delete=models.CASCADE,
        related_name="participants",
    )

    class Meta:
        ordering = ["full_name"]
        indexes = [models.Index(fields=["document_number"])]

    def __str__(self) -> str:
        return f"{self.full_name} - {self.registration.robot_name}"


class Institution(TimeStampedModel):
    name = models.CharField(max_length=180, unique=True)
    institution_type = models.CharField(max_length=20, choices=InstitutionType.choices)
    city = models.CharField(max_length=120, blank=True)
    department = models.CharField(max_length=120, blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=30, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.name} ({self.get_institution_type_display()})"


class Team(TimeStampedModel):
    edition = models.ForeignKey(
        "tournament.TournamentEdition",
        on_delete=models.PROTECT,
        related_name="teams",
    )
    name = models.CharField(max_length=120)
    institution = models.ForeignKey(Institution, on_delete=models.PROTECT, related_name="teams")
    category_label = models.CharField(
        max_length=120,
        help_text="Categoria operativa visible para el torneo. Ej: Junior, Senior, Universitaria."
    )
    robot_name = models.CharField(max_length=120)
    robot_weight_grams = models.PositiveIntegerField(null=True, blank=True)
    coach_name = models.CharField(max_length=120)
    coach_email = models.EmailField(validators=[EmailValidator()])
    coach_phone = models.CharField(
        max_length=20,
        validators=[RegexValidator(r"^[0-9+\\-\\s]{7,20}$", "Ingresa un telefono valido.")],
    )
    emergency_contact = models.CharField(max_length=120, blank=True)
    emergency_phone = models.CharField(max_length=20, blank=True)
    status = models.CharField(
        max_length=20,
        choices=RegistrationStatus.choices,
        default=RegistrationStatus.SUBMITTED,
    )
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["edition", "status"]),
            models.Index(fields=["status"]),
            models.Index(fields=["institution", "category_label"]),
        ]
        constraints = [
            models.UniqueConstraint(fields=["edition", "institution", "name"], name="unique_team_per_edition"),
        ]

    def __str__(self) -> str:
        return self.name


class TeamMember(TimeStampedModel):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="members")
    full_name = models.CharField(max_length=120)
    document_number = models.CharField(max_length=30, unique=True)
    email = models.EmailField(blank=True)
    age = models.PositiveSmallIntegerField()
    role = models.CharField(
        max_length=80,
        help_text="Ej: conductor, programador, diseno, soporte."
    )
    is_team_lead = models.BooleanField(default=False)

    class Meta:
        ordering = ["full_name"]
        indexes = [models.Index(fields=["document_number"])]

    def __str__(self) -> str:
        return f"{self.full_name} - {self.team.name}"
