from django.conf import settings
from django.db import models

from apps.common.models import TimeStampedModel


class CommunicationType(models.TextChoices):
    SCHOOL = "colegio", "Colegio"
    UNIVERSITY = "universidad", "Universidad"
    SPONSOR = "patrocinador", "Patrocinador"
    ATTENDANCE = "asistencia", "Asistencia"
    GENERAL = "general", "General"


class CommunicationStatus(models.TextChoices):
    DRAFT = "draft", "Borrador"
    PREVIEWED = "previewed", "Previsualizado"
    SENDING = "sending", "En envio"
    SENT = "sent", "Enviado"
    FAILED = "failed", "Fallido"
    CANCELLED = "cancelled", "Cancelado"


class CommunicationLogStatus(models.TextChoices):
    PENDING = "pending", "Pendiente"
    SENT = "sent", "Enviado"
    TEST_SENT = "test_sent", "Prueba enviada"
    SKIPPED = "skipped", "Omitido"
    FAILED = "failed", "Fallido"
    DRY_RUN = "dry_run", "Simulado"


class CommunicationSendMode(models.TextChoices):
    DRY_RUN = "dry_run", "Simulacion segura"
    TEST = "test", "Prueba controlada"
    OFFICIAL = "official", "Envio oficial"


class CommunicationTemplate(TimeStampedModel):
    name = models.CharField(max_length=160)
    template_type = models.CharField(max_length=24, choices=CommunicationType.choices)
    file = models.FileField(upload_to="communication_templates/")
    required_markers = models.JSONField(default=list, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=False)
    validation_errors = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ["template_type", "-is_active", "name"]
        indexes = [
            models.Index(fields=["template_type", "is_active"]),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.get_template_type_display()})"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.is_active:
            CommunicationTemplate.objects.filter(template_type=self.template_type, is_active=True).exclude(pk=self.pk).update(
                is_active=False
            )


class CommunicationRecipient(TimeStampedModel):
    name = models.CharField(max_length=180)
    email = models.EmailField()
    recipient_type = models.CharField(max_length=24, choices=CommunicationType.choices)
    institution_name = models.CharField(max_length=180, blank=True)
    extra_data = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["recipient_type"]),
            models.Index(fields=["email"]),
        ]

    def __str__(self) -> str:
        return f"{self.name} <{self.email}>"


class CommunicationBatch(TimeStampedModel):
    name = models.CharField(max_length=180)
    communication_type = models.CharField(max_length=24, choices=CommunicationType.choices)
    template = models.ForeignKey(
        CommunicationTemplate,
        on_delete=models.SET_NULL,
        related_name="batches",
        null=True,
        blank=True,
    )
    status = models.CharField(
        max_length=24,
        choices=CommunicationStatus.choices,
        default=CommunicationStatus.DRAFT,
    )
    send_mode = models.CharField(
        max_length=24,
        choices=CommunicationSendMode.choices,
        default=CommunicationSendMode.DRY_RUN,
    )
    dry_run = models.BooleanField(default=True)
    test_recipient = models.EmailField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="communication_batches",
        null=True,
        blank=True,
    )
    sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["communication_type", "status"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self) -> str:
        return self.name


class CommunicationLog(TimeStampedModel):
    batch = models.ForeignKey(
        CommunicationBatch,
        on_delete=models.CASCADE,
        related_name="logs",
        null=True,
        blank=True,
    )
    recipient_name = models.CharField(max_length=180)
    recipient_email = models.EmailField(blank=True)
    original_recipient_email = models.EmailField(blank=True)
    physical_recipient_email = models.EmailField(blank=True)
    communication_type = models.CharField(max_length=24, choices=CommunicationType.choices)
    subject = models.CharField(max_length=220, blank=True)
    status = models.CharField(
        max_length=24,
        choices=CommunicationLogStatus.choices,
        default=CommunicationLogStatus.PENDING,
    )
    error_message = models.TextField(blank=True)
    rendered_preview = models.TextField(blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["communication_type", "status"]),
            models.Index(fields=["recipient_email"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.recipient_name} - {self.get_status_display()}"
