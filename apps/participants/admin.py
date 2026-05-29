from django.contrib import admin
from django.urls import reverse

from .models import (
    Institution,
    InstitutionType,
    SchoolParticipant,
    SchoolRegistration,
    Team,
    TeamMember,
    UniversityParticipant,
    UniversityRegistration,
)
from .services import send_attendance_confirmation_request_email, sync_registration_to_team


@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    list_display = ("name", "institution_type", "city", "department")
    search_fields = ("name", "city", "department")
    list_filter = ("institution_type",)


class TeamMemberInline(admin.TabularInline):
    model = TeamMember
    extra = 0


class SchoolParticipantInline(admin.TabularInline):
    model = SchoolParticipant
    extra = 0


class UniversityParticipantInline(admin.TabularInline):
    model = UniversityParticipant
    extra = 0


class RegistrationAdminMixin:
    actions = ["send_attendance_requests", "sync_confirmed_to_teams"]

    registration_type = ""
    institution_type = ""

    def send_attendance_requests(self, request, queryset):
        sent = 0
        skipped = 0
        for registration in queryset:
            if registration.attendance_confirmed_at:
                skipped += 1
                continue
            confirmation_url = request.build_absolute_uri(
                reverse("participants:attendance_confirmation", args=[registration.attendance_token])
            )
            try:
                send_attendance_confirmation_request_email(
                    registration,
                    self.registration_type,
                    confirmation_url,
                )
                sent += 1
            except Exception:
                skipped += 1
        self.message_user(
            request,
            f"Correos de confirmacion enviados: {sent}. Registros omitidos o con error: {skipped}.",
        )

    send_attendance_requests.short_description = "Enviar correo de confirmacion de asistencia"

    def sync_confirmed_to_teams(self, request, queryset):
        synced = 0
        skipped = 0
        for registration in queryset:
            if registration.attendance_confirmed_at is None:
                skipped += 1
                continue
            sync_registration_to_team(registration, self.institution_type)
            synced += 1
        self.message_user(
            request,
            f"Registros sincronizados a equipos: {synced}. Registros omitidos: {skipped}.",
        )

    sync_confirmed_to_teams.short_description = "Sincronizar confirmados al cuadro oficial"


@admin.register(SchoolRegistration)
class SchoolRegistrationAdmin(RegistrationAdminMixin, admin.ModelAdmin):
    list_display = (
        "institution_name",
        "robot_name",
        "responsible_name",
        "edition",
        "status",
        "attendance_request_sent_at",
        "attendance_confirmed_at",
    )
    list_filter = ("status", "edition")
    search_fields = ("institution_name", "robot_name", "responsible_name", "contact_email")
    inlines = [SchoolParticipantInline]
    registration_type = "colegio"
    institution_type = InstitutionType.SCHOOL


@admin.register(UniversityRegistration)
class UniversityRegistrationAdmin(RegistrationAdminMixin, admin.ModelAdmin):
    list_display = (
        "institution_name",
        "robot_name",
        "responsible_name",
        "edition",
        "status",
        "attendance_request_sent_at",
        "attendance_confirmed_at",
    )
    list_filter = ("status", "edition")
    search_fields = ("institution_name", "robot_name", "responsible_name", "contact_email")
    inlines = [UniversityParticipantInline]
    registration_type = "universidad"
    institution_type = InstitutionType.UNIVERSITY


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ("name", "edition", "institution", "category_label", "status")
    list_filter = ("status", "edition", "institution__institution_type")
    search_fields = ("name", "robot_name", "institution__name", "edition__name")
    inlines = [TeamMemberInline]
