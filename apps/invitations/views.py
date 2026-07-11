from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render

from apps.participants.models import RegistrationStatus, SchoolRegistration, UniversityRegistration

from .forms import CommunicationRecipientForm, CommunicationTemplateForm, InvitationBatchForm
from .models import (
    CommunicationBatch,
    CommunicationLog,
    CommunicationLogStatus,
    CommunicationRecipient,
    CommunicationSendMode,
    CommunicationTemplate,
)
from .services import (
    create_communication_batch,
    extract_docx_text_markers,
    is_real_email_configured,
    load_recipients_from_xlsx,
    mark_batch_finished,
    send_attendance_request_for_registration,
    send_rendered_invitation,
)


def is_organizer(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)


@login_required
@user_passes_test(is_organizer)
def dashboard(request):
    email_status = is_real_email_configured()
    pending_confirmations = (
        SchoolRegistration.objects.filter(
            status=RegistrationStatus.SUBMITTED,
            attendance_confirmed_at__isnull=True,
            attendance_request_sent_at__isnull=True,
        ).count()
        + UniversityRegistration.objects.filter(
            status=RegistrationStatus.SUBMITTED,
            attendance_confirmed_at__isnull=True,
            attendance_request_sent_at__isnull=True,
        ).count()
    )
    context = {
        "email_status": email_status,
        "active_templates": CommunicationTemplate.objects.filter(is_active=True).count(),
        "recipient_total": CommunicationRecipient.objects.count(),
        "dry_run_total": CommunicationLog.objects.filter(status=CommunicationLogStatus.DRY_RUN).count(),
        "test_sent_total": CommunicationLog.objects.filter(status=CommunicationLogStatus.TEST_SENT).count(),
        "sent_total": CommunicationLog.objects.filter(status=CommunicationLogStatus.SENT).count(),
        "failed_total": CommunicationLog.objects.filter(status=CommunicationLogStatus.FAILED).count(),
        "pending_confirmations": pending_confirmations,
        "recent_batches": CommunicationBatch.objects.select_related("template", "created_by")[:6],
    }
    return render(request, "invitations/dashboard.html", context)


@login_required
@user_passes_test(is_organizer)
def template_list(request):
    templates = CommunicationTemplate.objects.all()
    grouped = templates.values("template_type").annotate(total=Count("id"))
    return render(request, "invitations/template_list.html", {"templates": templates, "grouped": grouped})


@login_required
@user_passes_test(is_organizer)
def template_create(request):
    if request.method == "POST":
        form = CommunicationTemplateForm(request.POST, request.FILES)
        if form.is_valid():
            template = form.save()
            messages.success(request, f"Plantilla {template.name} guardada y validada.")
            return redirect("invitations:template_list")
    else:
        form = CommunicationTemplateForm()
    return render(request, "invitations/template_form.html", {"form": form})


@login_required
@user_passes_test(is_organizer)
def template_preview(request, template_id):
    template = get_object_or_404(CommunicationTemplate, pk=template_id)
    try:
        markers = extract_docx_text_markers(template.file)
    except Exception as error:
        markers = []
        messages.error(request, f"No fue posible leer la plantilla: {error}")
    return render(request, "invitations/template_preview.html", {"template": template, "markers": markers})


def _recipient_dict_from_model(recipient):
    return {
        "name": recipient.name,
        "email": recipient.email,
        "recipient_type": recipient.recipient_type,
        "institution_name": recipient.institution_name,
        "extra_data": recipient.extra_data or {},
    }


@login_required
@user_passes_test(is_organizer)
def invitations(request):
    batch = None
    if request.method == "POST" and request.POST.get("action") == "add_recipient":
        recipient_form = CommunicationRecipientForm(request.POST)
        invitation_form = InvitationBatchForm()
        if recipient_form.is_valid():
            recipient_form.save()
            messages.success(request, "Destinatario registrado.")
            return redirect("invitations:invitations")
    elif request.method == "POST":
        invitation_form = InvitationBatchForm(request.POST, request.FILES)
        recipient_form = CommunicationRecipientForm()
        if invitation_form.is_valid():
            communication_type = invitation_form.cleaned_data["communication_type"]
            template = invitation_form.cleaned_data["template"]
            send_mode = invitation_form.cleaned_data.get("send_mode")
            dry_run = send_mode == CommunicationSendMode.DRY_RUN
            test_recipient = invitation_form.cleaned_data.get("test_recipient", "").strip()
            if not template:
                messages.error(request, "Debes seleccionar una plantilla activa para procesar invitaciones.")
            else:
                recipients_file = invitation_form.cleaned_data.get("recipients_file")
                try:
                    if recipients_file:
                        recipients = load_recipients_from_xlsx(recipients_file)
                    else:
                        recipients = [
                            _recipient_dict_from_model(recipient)
                            for recipient in CommunicationRecipient.objects.filter(recipient_type=communication_type)
                        ]
                except ValueError as error:
                    messages.error(request, str(error))
                    recipients = []

                if recipients:
                    batch = create_communication_batch(
                        name=f"Invitaciones {template.get_template_type_display()}",
                        communication_type=communication_type,
                        template=template,
                        dry_run=dry_run,
                        send_mode=send_mode,
                        test_recipient=test_recipient,
                        created_by=request.user,
                    )
                    for recipient in recipients:
                        recipient_type = recipient.get("recipient_type") or communication_type
                        if communication_type != "general" and recipient_type != communication_type:
                            CommunicationLog.objects.create(
                                batch=batch,
                                recipient_name=recipient.get("name", ""),
                                recipient_email=recipient.get("email", ""),
                                communication_type=communication_type,
                                subject="Invitacion",
                                status=CommunicationLogStatus.SKIPPED,
                                error_message=f"Tipo de destinatario no coincide: {recipient_type}",
                            )
                            continue
                        send_rendered_invitation(
                            batch=batch,
                            template=template,
                            recipient=recipient,
                            communication_type=communication_type,
                            dry_run=dry_run,
                            test_recipient=test_recipient,
                            extra_data=recipient.get("extra_data") or {},
                        )
                    mark_batch_finished(batch)
                    if send_mode == CommunicationSendMode.TEST:
                        messages.success(request, "Lote procesado como prueba real controlada.")
                    elif dry_run:
                        messages.success(request, "Lote procesado en simulacion segura.")
                    else:
                        messages.success(request, "Lote procesado como envio real.")
                    return redirect("invitations:history")
                else:
                    messages.warning(request, "No hay destinatarios para procesar.")
    else:
        invitation_form = InvitationBatchForm()
        recipient_form = CommunicationRecipientForm()

    context = {
        "invitation_form": invitation_form,
        "recipient_form": recipient_form,
        "recipients": CommunicationRecipient.objects.all()[:80],
        "batch": batch,
        "email_status": is_real_email_configured(),
    }
    return render(request, "invitations/invitations.html", context)


def _confirmation_records():
    school_records = [
        {"registration": registration, "type": "colegio", "model": "school"}
        for registration in SchoolRegistration.objects.filter(status=RegistrationStatus.SUBMITTED).order_by("institution_name")
    ]
    university_records = [
        {"registration": registration, "type": "universidad", "model": "university"}
        for registration in UniversityRegistration.objects.filter(status=RegistrationStatus.SUBMITTED).order_by("institution_name")
    ]
    return school_records + university_records


@login_required
@user_passes_test(is_organizer)
def confirmations(request):
    if request.method == "POST":
        model_name = request.POST.get("model")
        registration_id = request.POST.get("registration_id")
        resend = request.POST.get("resend") == "yes"
        send_mode = request.POST.get("send_mode") or CommunicationSendMode.DRY_RUN
        dry_run = send_mode == CommunicationSendMode.DRY_RUN
        test_recipient = request.POST.get("test_recipient", "").strip()
        if send_mode == CommunicationSendMode.TEST and not test_recipient:
            messages.error(request, "Debes indicar el correo receptor de prueba controlada.")
            return redirect("invitations:confirmations")
        if send_mode in {CommunicationSendMode.TEST, CommunicationSendMode.OFFICIAL} and request.POST.get(
            "confirm_real_send"
        ) != "yes":
            messages.error(request, "Debes confirmar explicitamente el envio real.")
            return redirect("invitations:confirmations")
        if send_mode in {CommunicationSendMode.TEST, CommunicationSendMode.OFFICIAL}:
            email_status = is_real_email_configured()
            if not email_status.can_send_real:
                messages.error(request, email_status.message)
                return redirect("invitations:confirmations")

        Model = SchoolRegistration if model_name == "school" else UniversityRegistration
        registration_type = "colegio" if model_name == "school" else "universidad"
        registration = get_object_or_404(Model, pk=registration_id)
        if registration.attendance_request_sent_at and not resend:
            messages.warning(request, "La solicitud ya fue enviada. Usa reenvio explicito si necesitas repetirla.")
            return redirect("invitations:confirmations")

        confirmation_url = request.build_absolute_uri(
            f"/registro/confirmar-asistencia/{registration.attendance_token}/"
        )
        batch = create_communication_batch(
            name=f"Confirmacion asistencia {registration.robot_name}",
            communication_type="asistencia",
            dry_run=dry_run,
            send_mode=send_mode,
            test_recipient=test_recipient,
            created_by=request.user,
        )
        send_attendance_request_for_registration(
            batch=batch,
            registration=registration,
            registration_type=registration_type,
            confirmation_url=confirmation_url,
            dry_run=dry_run,
            test_recipient=test_recipient,
        )
        mark_batch_finished(batch)
        if send_mode == CommunicationSendMode.TEST:
            messages.success(request, "Solicitud enviada como prueba controlada.")
        elif dry_run:
            messages.success(request, "Solicitud simulada.")
        else:
            messages.success(request, "Solicitud enviada como envio real.")
        return redirect("invitations:confirmations")

    return render(
        request,
        "invitations/confirmations.html",
        {
            "records": _confirmation_records(),
            "email_status": is_real_email_configured(),
        },
    )


@login_required
@user_passes_test(is_organizer)
def history(request):
    batches = CommunicationBatch.objects.select_related("template", "created_by").prefetch_related("logs")[:40]
    logs = CommunicationLog.objects.select_related("batch")[:100]
    return render(request, "invitations/history.html", {"batches": batches, "logs": logs})
