import re
import unicodedata

from django import forms
from django.db import transaction

from apps.tournament.models import TournamentEdition
from .models import (
    RegistrationStatus,
    SchoolParticipant,
    SchoolRegistration,
    UniversityParticipant,
    UniversityRegistration,
)


def normalize_robot_name(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value or "").encode("ascii", "ignore").decode("ascii")
    normalized = normalized.lower().strip()
    normalized = re.sub(r"[^a-z0-9]+", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    numbered_variant = re.sub(r"(?:\s+\d+)+$", "", normalized).strip()
    return numbered_variant or normalized


def normalize_document_number(value: str) -> str:
    cleaned = unicodedata.normalize("NFKD", value or "").encode("ascii", "ignore").decode("ascii")
    cleaned = cleaned.lower().strip()
    cleaned = re.sub(r"[^a-z0-9]+", "", cleaned)
    return cleaned


class BaseRegistrationForm(forms.ModelForm):
    leader_name = forms.CharField(label="Nombre del integrante #1 (Lider de equipo)", max_length=120)
    leader_document_number = forms.CharField(label="Numero de documento de identidad del integrante #1", max_length=30)
    member_two_name = forms.CharField(label="Nombre del integrante #2", max_length=120, required=False)
    member_two_document_number = forms.CharField(
        label="Numero de documento de identidad del integrante #2",
        max_length=30,
        required=False,
    )
    member_three_name = forms.CharField(label="Nombre del integrante #3", max_length=120, required=False)
    member_three_document_number = forms.CharField(
        label="Numero de documento de identidad del integrante #3",
        max_length=30,
        required=False,
    )

    field_order = [
        "institution_name",
        "responsible_name",
        "robot_name",
        "leader_name",
        "contact_phone",
        "leader_document_number",
        "contact_email",
        "member_two_name",
        "member_two_document_number",
        "member_three_name",
        "member_three_document_number",
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["institution_name"].label = "Nombre de universidad o colegio"
        self.fields["responsible_name"].label = "Nombre del docente encargado o acudiente responsable"
        self.fields["robot_name"].label = "Nombre del robot"
        self.fields["robot_name"].help_text = (
            "Debe ser un nombre exclusivo. No se permiten variantes numeradas o parecidas como "
            "'Rayo McQueen 2' si ya existe 'Rayo McQueen'."
        )
        self.fields["contact_phone"].label = "Telefono de contacto"
        self.fields["contact_email"].label = "Correo electronico"

    def clean(self):
        cleaned_data = super().clean()
        edition = TournamentEdition.objects.filter(is_active=True).order_by("-start_date", "-created_at").first()
        if edition is None:
            raise forms.ValidationError(
                "No existe una edicion activa del torneo. Crea una desde el panel administrativo."
            )
        self.active_edition = edition

        if bool(cleaned_data.get("member_two_name")) != bool(cleaned_data.get("member_two_document_number")):
            raise forms.ValidationError(
                "Para el integrante #2 debes completar tanto el nombre como el numero de documento."
            )

        if bool(cleaned_data.get("member_three_name")) != bool(cleaned_data.get("member_three_document_number")):
            raise forms.ValidationError(
                "Para el integrante #3 debes completar tanto el nombre como el numero de documento."
            )

        robot_name = (cleaned_data.get("robot_name") or "").strip()
        contact_email = (cleaned_data.get("contact_email") or "").strip()
        document_fields = [
            ("leader_document_number", "integrante #1"),
            ("member_two_document_number", "integrante #2"),
            ("member_three_document_number", "integrante #3"),
        ]
        submitted_documents = {
            field_name: normalize_document_number(cleaned_data.get(field_name) or "")
            for field_name, _label in document_fields
            if cleaned_data.get(field_name)
        }

        if robot_name:
            normalized_robot = normalize_robot_name(robot_name)
            existing_robot_names = list(
                SchoolRegistration.objects.filter(edition=edition).values_list("robot_name", flat=True)
            ) + list(UniversityRegistration.objects.filter(edition=edition).values_list("robot_name", flat=True))
            duplicate_robot = any(normalize_robot_name(existing_name) == normalized_robot for existing_name in existing_robot_names)
            if duplicate_robot:
                self.add_error(
                    "robot_name",
                    "Ese nombre ya esta reservado en la edicion activa o es demasiado parecido a otro robot existente.",
                )

        if contact_email:
            duplicate_email = (
                SchoolRegistration.objects.filter(edition=edition, contact_email__iexact=contact_email).exists()
                or UniversityRegistration.objects.filter(edition=edition, contact_email__iexact=contact_email).exists()
            )
            if duplicate_email:
                self.add_error(
                    "contact_email",
                    "Este correo ya fue usado para una inscripcion en la edicion activa.",
                )

        seen_documents = {}
        for field_name, label in document_fields:
            document_value = submitted_documents.get(field_name)
            if not document_value:
                continue
            if document_value in seen_documents:
                self.add_error(
                    field_name,
                    f"Este documento ya fue escrito en el formulario para {seen_documents[document_value]}.",
                )
            else:
                seen_documents[document_value] = label

        if submitted_documents:
            existing_documents = list(
                SchoolParticipant.objects.filter(registration__edition=edition).values_list("document_number", flat=True)
            ) + list(
                UniversityParticipant.objects.filter(registration__edition=edition).values_list("document_number", flat=True)
            )
            existing_documents = {normalize_document_number(document) for document in existing_documents}
            for field_name, label in document_fields:
                document_value = submitted_documents.get(field_name)
                if document_value and document_value in existing_documents:
                    self.add_error(
                        field_name,
                        f"El documento del {label} ya aparece en otra inscripcion de la edicion activa.",
                    )
        return cleaned_data

    @transaction.atomic
    def save(self, commit=True):
        registration = super().save(commit=False)
        registration.edition = self.active_edition
        registration.status = RegistrationStatus.SUBMITTED
        if commit:
            registration.save()
            registration.participants.all().delete()
            self.participant_model.objects.create(
                registration=registration,
                full_name=self.cleaned_data["leader_name"],
                document_number=self.cleaned_data["leader_document_number"],
                role="lider",
                is_team_lead=True,
            )
            if self.cleaned_data.get("member_two_name"):
                self.participant_model.objects.create(
                    registration=registration,
                    full_name=self.cleaned_data["member_two_name"],
                    document_number=self.cleaned_data["member_two_document_number"],
                    role="integrante 2",
                    is_team_lead=False,
                )
            if self.cleaned_data.get("member_three_name"):
                self.participant_model.objects.create(
                    registration=registration,
                    full_name=self.cleaned_data["member_three_name"],
                    document_number=self.cleaned_data["member_three_document_number"],
                    role="integrante 3",
                    is_team_lead=False,
                )
        return registration


class SchoolRegistrationForm(BaseRegistrationForm):
    participant_model = SchoolParticipant

    class Meta:
        model = SchoolRegistration
        fields = [
            "institution_name",
            "responsible_name",
            "robot_name",
            "contact_phone",
            "contact_email",
        ]

    field_order = [
        "institution_name",
        "responsible_name",
        "robot_name",
        "leader_name",
        "contact_phone",
        "leader_document_number",
        "contact_email",
        "member_two_name",
        "member_two_document_number",
        "member_three_name",
        "member_three_document_number",
    ]


class UniversityRegistrationForm(BaseRegistrationForm):
    participant_model = UniversityParticipant
    semester = forms.IntegerField(
        label="Semestre actual",
        min_value=1,
        help_text="Solo pueden participar estudiantes de hasta cuarto semestre.",
    )

    class Meta:
        model = UniversityRegistration
        fields = [
            "institution_name",
            "responsible_name",
            "robot_name",
            "semester",
            "contact_phone",
            "contact_email",
        ]

    field_order = [
        "institution_name",
        "responsible_name",
        "robot_name",
        "semester",
        "leader_name",
        "contact_phone",
        "leader_document_number",
        "contact_email",
        "member_two_name",
        "member_two_document_number",
        "member_three_name",
        "member_three_document_number",
    ]

    def clean(self):
        cleaned_data = super().clean()
        semester = cleaned_data.get("semester")
        if semester is not None and semester > 4:
            self.add_error(
                "semester",
                "Los equipos universitarios solo pueden participar hasta cuarto semestre.",
            )
        return cleaned_data
