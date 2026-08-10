from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from django.utils import timezone

from .models import Institution, InstitutionType, RegistrationStatus, Team, TeamMember


def registration_type_labels(registration_type: str) -> tuple[str, str]:
    if registration_type == "colegio":
        return "colegio", "Colegios"
    return "universidad", "Universidades"


def send_registration_received_email(registration, registration_type: str) -> None:
    category_label, _team_category = registration_type_labels(registration_type)
    subject = "Registro recibido - Torneo Robot Explota Globos"
    message = (
        f"Hola,\n\n"
        f"Hemos recibido correctamente tu registro en la categoria {category_label}.\n\n"
        f"Robot: {registration.robot_name}\n"
        f"Institucion: {registration.institution_name}\n"
        f"Responsable: {registration.responsible_name}\n\n"
        f"Tu informacion quedo guardada en la plataforma y tu registro ya aparece como recibido.\n"
        f"Por favor permanece atento a proximos correos, porque antes del torneo te enviaremos la "
        f"solicitud de confirmacion de asistencia. Si no confirmas asistencia, el robot no sera tenido en cuenta "
        f"para el cuadro oficial del evento.\n\n"
        f"Torneo Robot Explota Globos\n"
        f"Universidad Tecnologica de Pereira"
    )
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[registration.contact_email],
        fail_silently=False,
    )
    registration.receipt_email_sent_at = timezone.now()
    registration.save(update_fields=["receipt_email_sent_at", "updated_at"])


def send_attendance_confirmation_request_email(registration, registration_type: str, confirmation_url: str) -> None:
    category_label, _team_category = registration_type_labels(registration_type)
    subject = "Confirma tu asistencia - Torneo Robot Explota Globos"
    message = (
        f"Hola,\n\n"
        f"Ya estamos en la etapa de confirmacion de asistencia para el torneo.\n\n"
        f"Robot: {registration.robot_name}\n"
        f"Categoria: {category_label}\n"
        f"Institucion: {registration.institution_name}\n\n"
        f"Para confirmar que asistirás al evento, entra al siguiente enlace:\n"
        f"{confirmation_url}\n\n"
        f"Solo los robots que confirmen asistencia seran tenidos en cuenta para generar el cuadro oficial de fases.\n\n"
        f"Torneo Robot Explota Globos\n"
        f"Universidad Tecnologica de Pereira"
    )
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[registration.contact_email],
        fail_silently=False,
    )
    registration.attendance_request_sent_at = timezone.now()
    registration.save(update_fields=["attendance_request_sent_at", "updated_at"])


def send_attendance_confirmed_email(registration, registration_type: str) -> None:
    category_label, _team_category = registration_type_labels(registration_type)
    subject = "Asistencia confirmada - Torneo Robot Explota Globos"
    message = (
        f"Hola,\n\n"
        f"Tu asistencia quedo confirmada correctamente para la categoria {category_label}.\n\n"
        f"Robot: {registration.robot_name}\n"
        f"Institucion: {registration.institution_name}\n\n"
        f"Desde este momento tu robot ya puede ser tenido en cuenta para el cuadro oficial del torneo.\n"
        f"Pronto recibirás mas informacion operativa del evento.\n\n"
        f"Torneo Robot Explota Globos\n"
        f"Universidad Tecnologica de Pereira"
    )
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[registration.contact_email],
        fail_silently=False,
    )


@transaction.atomic
def sync_registration_to_team(registration, institution_type: str):
    _category_label, team_category = registration_type_labels(
        "colegio" if institution_type == InstitutionType.SCHOOL else "universidad"
    )
    from apps.tournament.models import DivisionCompetition, DivisionType
    from apps.tournament.services import competition_has_started_flow

    division = DivisionType.SCHOOL if institution_type == InstitutionType.SCHOOL else DivisionType.UNIVERSITY
    competition = DivisionCompetition.objects.select_for_update().filter(
        edition=registration.edition,
        division=division,
    ).first()
    institution = Institution.objects.filter(name=registration.institution_name).first()
    if institution is not None and institution.institution_type != institution_type:
        raise ValueError(
            "La institucion ya existe con una categoria diferente. "
            "Revisa el registro antes de sincronizarlo al cuadro oficial."
        )
    existing_team = (
        Team.objects.filter(
            edition=registration.edition,
            institution=institution,
            name=registration.robot_name,
        ).first()
        if institution is not None
        else None
    )
    if competition and competition_has_started_flow(competition):
        team_is_in_bracket = (
            existing_team is not None
            and competition.groups.filter(entries__team=existing_team).exists()
        )
        if not team_is_in_bracket:
            raise ValueError(
                "La competencia ya tiene progreso. Este equipo no puede agregarse al cuadro "
                "sin una decision operativa explicita."
            )
    if institution is None:
        institution = Institution.objects.create(
            name=registration.institution_name,
            institution_type=institution_type,
        )

    team, _created = Team.objects.update_or_create(
        edition=registration.edition,
        institution=institution,
        name=registration.robot_name,
        defaults={
            "category_label": team_category,
            "robot_name": registration.robot_name,
            "coach_name": registration.responsible_name,
            "coach_email": registration.contact_email,
            "coach_phone": registration.contact_phone,
            "status": RegistrationStatus.APPROVED,
            "notes": "Equipo creado automaticamente despues de confirmar asistencia.",
        },
    )
    team.members.all().delete()
    TeamMember.objects.bulk_create(
        [
            TeamMember(
                team=team,
                full_name=participant.full_name,
                document_number=participant.document_number,
                email=registration.contact_email if participant.is_team_lead else "",
                age=18 if institution_type == InstitutionType.UNIVERSITY else 15,
                role=participant.role or ("lider" if participant.is_team_lead else "integrante"),
                is_team_lead=participant.is_team_lead,
            )
            for participant in registration.participants.all()
        ]
    )
    registration.team_synced_at = timezone.now()
    registration.save(update_fields=["team_synced_at", "updated_at"])
    return team


@transaction.atomic
def confirm_attendance(registration, registration_type: str, institution_type: str):
    registration = (
        type(registration).objects.select_for_update().get(pk=registration.pk)
    )
    if registration.attendance_confirmed_at:
        return sync_registration_to_team(registration, institution_type)

    registration.attendance_confirmed_at = timezone.now()
    registration.status = RegistrationStatus.APPROVED
    registration.save(update_fields=["attendance_confirmed_at", "status", "updated_at"])
    team = sync_registration_to_team(registration, institution_type)
    from apps.tournament.models import CompetitionStatus, DivisionCompetition, DivisionType
    from apps.tournament.services import initialize_competition

    division = DivisionType.SCHOOL if institution_type == InstitutionType.SCHOOL else DivisionType.UNIVERSITY
    competition = DivisionCompetition.objects.filter(edition=registration.edition, division=division).first()
    if competition is None or competition.status == CompetitionStatus.DRAFT:
        initialize_competition(registration.edition, division)
    try:
        send_attendance_confirmed_email(registration, registration_type)
    except Exception:
        pass
    return team
