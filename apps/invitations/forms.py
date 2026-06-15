from django import forms
from django.core.exceptions import ValidationError

from .models import CommunicationRecipient, CommunicationSendMode, CommunicationTemplate, CommunicationType
from .services import parse_required_markers, validate_template_markers


MAX_TEMPLATE_SIZE = 8 * 1024 * 1024


class CommunicationTemplateForm(forms.ModelForm):
    required_markers_text = forms.CharField(
        label="Marcadores requeridos",
        required=False,
        widget=forms.Textarea(attrs={"rows": 4}),
        help_text="Uno por linea o separados por coma. Ej: {{NOMBRE}}, {{INSTITUCION}}, {{EVENTO}}.",
    )

    class Meta:
        model = CommunicationTemplate
        fields = ["name", "template_type", "file", "required_markers_text", "description", "is_active"]
        labels = {
            "name": "Nombre",
            "template_type": "Tipo",
            "file": "Archivo .docx",
            "description": "Descripcion",
            "is_active": "Activar para este tipo",
        }
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields["required_markers_text"].initial = "\n".join(self.instance.required_markers or [])

    def clean_file(self):
        file = self.cleaned_data.get("file")
        if not file:
            return file
        if not file.name.lower().endswith(".docx"):
            raise ValidationError("Solo se permiten plantillas .docx.")
        if file.size > MAX_TEMPLATE_SIZE:
            raise ValidationError("La plantilla supera el tamano maximo de 8 MB.")
        return file

    def clean_required_markers_text(self):
        return parse_required_markers(self.cleaned_data.get("required_markers_text", ""))

    def clean(self):
        cleaned_data = super().clean()
        required_markers = cleaned_data.get("required_markers_text") or []
        file = cleaned_data.get("file")
        if file and required_markers:
            missing = validate_template_markers(file, required_markers)
            if hasattr(file, "seek"):
                file.seek(0)
            if missing:
                self.add_error(
                    "required_markers_text",
                    "Faltan marcadores en la plantilla: " + ", ".join(missing),
                )
                cleaned_data["validation_errors"] = missing
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.required_markers = self.cleaned_data.get("required_markers_text") or []
        instance.validation_errors = self.cleaned_data.get("validation_errors", [])
        if commit:
            instance.save()
            self.save_m2m()
        return instance


class CommunicationRecipientForm(forms.ModelForm):
    class Meta:
        model = CommunicationRecipient
        fields = ["name", "email", "recipient_type", "institution_name", "extra_data"]
        labels = {
            "name": "Nombre",
            "email": "Correo",
            "recipient_type": "Tipo",
            "institution_name": "Institucion",
            "extra_data": "Datos extra para marcadores",
        }
        widgets = {
            "extra_data": forms.Textarea(attrs={"rows": 4}),
        }


class InvitationBatchForm(forms.Form):
    communication_type = forms.ChoiceField(
        label="Tipo de invitacion",
        choices=[
            (CommunicationType.SCHOOL, "Colegio"),
            (CommunicationType.UNIVERSITY, "Universidad"),
            (CommunicationType.SPONSOR, "Patrocinador"),
            (CommunicationType.GENERAL, "General"),
        ],
    )
    template = forms.ModelChoiceField(
        label="Plantilla",
        queryset=CommunicationTemplate.objects.none(),
        required=False,
        help_text="Si se deja vacio se usara la plantilla activa del tipo elegido.",
    )
    recipients_file = forms.FileField(
        label="Excel de destinatarios",
        required=False,
        help_text="Columnas: NOMBRE, CORREO, TIPO, INSTITUCION opcional.",
    )
    send_mode = forms.ChoiceField(
        label="Modo de envio",
        choices=CommunicationSendMode.choices,
        initial=CommunicationSendMode.DRY_RUN,
        help_text="La simulacion no envia correos. La prueba controlada envia todo a un correo de prueba.",
    )
    test_recipient = forms.EmailField(
        label="Correo para prueba controlada",
        required=False,
        help_text="Obligatorio si eliges prueba controlada.",
    )
    confirm_real_send = forms.BooleanField(
        label="Confirmo que quiero enviar correos reales",
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["template"].queryset = CommunicationTemplate.objects.filter(is_active=True).order_by("template_type", "name")

    def clean_recipients_file(self):
        file = self.cleaned_data.get("recipients_file")
        if not file:
            return file
        if not file.name.lower().endswith(".xlsx"):
            raise ValidationError("Solo se permite importar destinatarios desde .xlsx.")
        if file.size > 4 * 1024 * 1024:
            raise ValidationError("El archivo supera el tamano maximo de 4 MB.")
        return file

    def clean(self):
        cleaned_data = super().clean()
        send_mode = cleaned_data.get("send_mode")
        if send_mode == CommunicationSendMode.TEST and not cleaned_data.get("test_recipient"):
            self.add_error("test_recipient", "Debes indicar el correo de prueba.")
        if send_mode in {CommunicationSendMode.TEST, CommunicationSendMode.OFFICIAL} and not cleaned_data.get(
            "confirm_real_send"
        ):
            self.add_error("confirm_real_send", "Debes confirmar explicitamente el envio real.")
        return cleaned_data
