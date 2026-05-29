from django.contrib import messages
from django.shortcuts import redirect, render

from .forms import SchoolRegistrationForm, UniversityRegistrationForm
from .models import InstitutionType, SchoolRegistration, UniversityRegistration
from .services import (
    confirm_attendance,
    send_registration_received_email,
)


def registration_choice(request):
    return render(
        request,
        "participants/registration_choice.html",
        {},
    )


def school_register(request):
    if request.method == "POST":
        form = SchoolRegistrationForm(request.POST)
        if form.is_valid():
            registration = form.save()
            try:
                send_registration_received_email(registration, "colegio")
                messages.success(
                    request,
                    "La inscripcion de colegio fue recibida correctamente y se envio un correo de registro.",
                )
            except Exception:
                messages.warning(
                    request,
                    "La inscripcion fue guardada, pero no se pudo enviar el correo de registro. Revisa la configuracion de correo.",
                )
            return redirect("participants:registration_success", registration_type="colegio")
    else:
        form = SchoolRegistrationForm()

    context = {
        "form": form,
        "title": "Registro de colegios",
        "subtitle": "Completa el registro escolar. El lider es obligatorio y los integrantes 2 y 3 son opcionales.",
        "registration_type": "Colegio",
        "form_intro": "Cada inscripcion corresponde a un robot.",
    }
    return render(request, "participants/registration_form.html", context)


def university_register(request):
    if request.method == "POST":
        form = UniversityRegistrationForm(request.POST)
        if form.is_valid():
            registration = form.save()
            try:
                send_registration_received_email(registration, "universidad")
                messages.success(
                    request,
                    "La inscripcion universitaria fue recibida correctamente y se envio un correo de registro.",
                )
            except Exception:
                messages.warning(
                    request,
                    "La inscripcion fue guardada, pero no se pudo enviar el correo de registro. Revisa la configuracion de correo.",
                )
            return redirect("participants:registration_success", registration_type="universidad")
    else:
        form = UniversityRegistrationForm()

    context = {
        "form": form,
        "title": "Registro de universidades",
        "subtitle": "Completa el registro universitario. El lider es obligatorio y los integrantes 2 y 3 son opcionales.",
        "registration_type": "Universidad",
        "form_intro": "Cada inscripcion corresponde a un robot.",
    }
    return render(request, "participants/registration_form.html", context)


def registration_success(request, registration_type):
    return render(
        request,
        "participants/registration_success.html",
        {"registration_type": registration_type},
    )


def resolve_registration_by_token(token):
    registration = SchoolRegistration.objects.filter(attendance_token=token).prefetch_related("participants").first()
    if registration:
        return registration, "colegio", InstitutionType.SCHOOL

    registration = UniversityRegistration.objects.filter(attendance_token=token).prefetch_related("participants").first()
    if registration:
        return registration, "universidad", InstitutionType.UNIVERSITY
    return None, None, None


def attendance_confirmation(request, token):
    registration, registration_type, institution_type = resolve_registration_by_token(token)
    if registration is None:
        return render(request, "participants/attendance_not_found.html", status=404)

    if request.method == "POST" and registration.attendance_confirmed_at is None:
        try:
            confirm_attendance(registration, registration_type, institution_type)
            messages.success(request, "La asistencia quedo confirmada correctamente.")
            return redirect("participants:attendance_confirmation", token=token)
        except Exception:
            messages.error(
                request,
                "No fue posible confirmar la asistencia en este momento. Intenta nuevamente o contacta a la organizacion.",
            )

    return render(
        request,
        "participants/attendance_confirmation.html",
        {
            "registration": registration,
            "registration_type": registration_type,
            "already_confirmed": registration.attendance_confirmed_at is not None,
        },
    )
