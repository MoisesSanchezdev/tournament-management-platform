from django.core.management.base import BaseCommand, CommandError

from collections import Counter

from django.core.validators import validate_email
from django.core.exceptions import ValidationError

from apps.invitations.models import CommunicationLog, CommunicationLogStatus, CommunicationSendMode, CommunicationTemplate
from apps.invitations.services import (
    active_template_for,
    create_communication_batch,
    is_real_email_configured,
    load_recipients_from_xlsx,
    mark_batch_finished,
    send_rendered_invitation,
)


class Command(BaseCommand):
    help = "Procesa invitaciones personalizadas desde Excel. Dry-run por defecto; envio real solo con --yes."

    def add_arguments(self, parser):
        parser.add_argument("--file", type=str, required=True, help="Excel con columnas NOMBRE, CORREO, TIPO e INSTITUCION opcional.")
        parser.add_argument("--template-id", type=int, help="ID de plantilla especifica. Si se omite usa la activa por tipo.")
        parser.add_argument("--yes", action="store_true", help="Confirma envio real. Sin este flag solo simula.")
        parser.add_argument("--dry-run", action="store_true", help="Mantiene simulacion aunque se pase por compatibilidad.")
        parser.add_argument(
            "--test-recipient",
            type=str,
            default="",
            help="Envia fisicamente todos los correos a este destinatario de prueba. Requiere --yes y SMTP completo.",
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
        email_status = is_real_email_configured()
        if not dry_run and not email_status.can_send_real:
            raise CommandError(email_status.message)

        try:
            recipients = load_recipients_from_xlsx(options["file"])
        except Exception as error:
            raise CommandError(str(error)) from error

        selected_template = None
        if options.get("template_id"):
            selected_template = CommunicationTemplate.objects.filter(pk=options["template_id"]).first()
            if selected_template is None:
                raise CommandError("No existe la plantilla indicada.")

        batch = create_communication_batch(
            name=f"Invitaciones desde {options['file']}",
            communication_type="general",
            template=selected_template,
            dry_run=dry_run,
            send_mode=send_mode,
            test_recipient=test_recipient,
        )

        for recipient in recipients:
            recipient_type = recipient.get("recipient_type") or "general"
            template = selected_template or active_template_for(recipient_type)
            if template is None:
                CommunicationLog.objects.create(
                    batch=batch,
                    recipient_name=recipient.get("name", ""),
                    recipient_email=recipient.get("email", ""),
                    communication_type=recipient_type,
                    subject="Invitacion",
                    status=CommunicationLogStatus.SKIPPED,
                    error_message=f"No hay plantilla activa para {recipient_type}.",
                )
                continue
            send_rendered_invitation(
                batch=batch,
                template=template,
                recipient=recipient,
                communication_type=recipient_type,
                dry_run=dry_run,
                test_recipient=test_recipient,
                extra_data=recipient.get("extra_data") or {},
            )

        mark_batch_finished(batch)
        skipped_reasons = Counter(
            batch.logs.filter(status=CommunicationLogStatus.SKIPPED)
            .exclude(error_message="")
            .values_list("error_message", flat=True)
        )
        mode_label = {
            CommunicationSendMode.DRY_RUN: "SIMULACION SEGURA",
            CommunicationSendMode.TEST: "PRUEBA REAL CONTROLADA",
            CommunicationSendMode.OFFICIAL: "ENVIO REAL OFICIAL",
        }[send_mode]
        self.stdout.write(f"Modo: {mode_label}")
        self.stdout.write(f"Correos reales enviados: {batch.logs.filter(status=CommunicationLogStatus.SENT).count()}")
        self.stdout.write(f"Correos de prueba enviados: {batch.logs.filter(status=CommunicationLogStatus.TEST_SENT).count()}")
        self.stdout.write(f"Correos simulados: {batch.logs.filter(status=CommunicationLogStatus.DRY_RUN).count()}")
        self.stdout.write(f"Omitidos: {batch.logs.filter(status=CommunicationLogStatus.SKIPPED).count()}")
        self.stdout.write(f"Fallidos: {batch.logs.filter(status=CommunicationLogStatus.FAILED).count()}")
        if skipped_reasons:
            self.stdout.write(f"Motivo principal de omision: {skipped_reasons.most_common(1)[0][0]}")
        if test_recipient:
            self.stdout.write(f"Destinatario fisico de prueba: {test_recipient}")
        self.stdout.write(f"Lote: {batch.id}")
