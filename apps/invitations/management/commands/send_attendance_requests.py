from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.core.validators import validate_email

from apps.invitations.models import CommunicationLogStatus, CommunicationSendMode
from apps.invitations.services import (
    create_communication_batch,
    is_real_email_configured,
    mark_batch_finished,
    send_attendance_request_for_registration,
)
from apps.participants.models import RegistrationStatus, SchoolRegistration, UniversityRegistration


class Command(BaseCommand):
    help = "Envia solicitudes de confirmacion de asistencia. Dry-run por defecto; envio real solo con --yes."

    def add_arguments(self, parser):
        parser.add_argument("--base-url", type=str, default="https://explotaglobos.com", help="URL base del sitio.")
        parser.add_argument("--yes", action="store_true", help="Confirma envio real.")
        parser.add_argument("--dry-run", action="store_true", help="Mantiene simulacion aunque se pase por compatibilidad.")
        parser.add_argument("--resend", action="store_true", help="Permite reenviar solicitudes ya enviadas.")
        parser.add_argument(
            "--test-recipient",
            type=str,
            default="",
            help="Envia fisicamente todas las solicitudes a este destinatario de prueba. Requiere --yes.",
        )

    def handle(self, *args, **options):
        test_recipient = options["test_recipient"].strip()
        if test_recipient and not options["yes"]:
            raise CommandError("--test-recipient requiere --yes para confirmar la prueba real controlada.")
        if test_recipient:
            try:
                validate_email(test_recipient)
            except ValidationError as error:
                raise CommandError("El correo de prueba no es valido.") from error

        dry_run = (not options["yes"] or options["dry_run"]) and not test_recipient
        send_mode = (
            CommunicationSendMode.TEST
            if test_recipient
            else CommunicationSendMode.DRY_RUN
            if dry_run
            else CommunicationSendMode.OFFICIAL
        )
        base_url = options["base_url"].rstrip("/")
        resend = options["resend"]
        email_status = is_real_email_configured()
        if not dry_run and not email_status.can_send_real:
            raise CommandError(email_status.message)

        batch = create_communication_batch(
            name=f"Solicitudes de asistencia {base_url}",
            communication_type="asistencia",
            dry_run=dry_run,
            send_mode=send_mode,
            test_recipient=test_recipient,
        )
        grupos = [
            (SchoolRegistration, "colegio"),
            (UniversityRegistration, "universidad"),
        ]

        for Model, registration_type in grupos:
            filters = {
                "status": RegistrationStatus.SUBMITTED,
                "attendance_confirmed_at__isnull": True,
            }
            if not resend:
                filters["attendance_request_sent_at__isnull"] = True
            registros = Model.objects.filter(**filters)
            self.stdout.write(f"{registration_type}: {registros.count()} pendientes")
            for registration in registros:
                confirmation_url = f"{base_url}/registro/confirmar-asistencia/{registration.attendance_token}/"
                send_attendance_request_for_registration(
                    batch=batch,
                    registration=registration,
                    registration_type=registration_type,
                    confirmation_url=confirmation_url,
                    dry_run=dry_run,
                    test_recipient=test_recipient,
                )

        mark_batch_finished(batch)
        sent = batch.logs.filter(status=CommunicationLogStatus.SENT).count()
        test_sent = batch.logs.filter(status=CommunicationLogStatus.TEST_SENT).count()
        simulated = batch.logs.filter(status=CommunicationLogStatus.DRY_RUN).count()
        failed = batch.logs.filter(status=CommunicationLogStatus.FAILED).count()
        skipped = batch.logs.filter(status=CommunicationLogStatus.SKIPPED).count()
        mode_label = {
            CommunicationSendMode.DRY_RUN: "SIMULACION SEGURA",
            CommunicationSendMode.TEST: "PRUEBA REAL CONTROLADA",
            CommunicationSendMode.OFFICIAL: "ENVIO REAL OFICIAL",
        }[send_mode]
        self.stdout.write(f"Modo: {mode_label}")
        self.stdout.write(f"Correos reales enviados: {sent}")
        self.stdout.write(f"Correos de prueba enviados: {test_sent}")
        self.stdout.write(f"Correos simulados: {simulated}")
        self.stdout.write(f"Omitidos: {skipped}")
        self.stdout.write(f"Fallidos: {failed}")
        if test_recipient:
            self.stdout.write(f"Destinatario fisico de prueba: {test_recipient}")
        self.stdout.write(f"Lote: {batch.id}")
