from django.contrib import admin

from .models import CommunicationBatch, CommunicationLog, CommunicationRecipient, CommunicationTemplate


@admin.register(CommunicationTemplate)
class CommunicationTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "template_type", "is_active", "updated_at")
    list_filter = ("template_type", "is_active")
    search_fields = ("name", "description")
    readonly_fields = ("validation_errors", "created_at", "updated_at")


@admin.register(CommunicationRecipient)
class CommunicationRecipientAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "recipient_type", "institution_name", "created_at")
    list_filter = ("recipient_type",)
    search_fields = ("name", "email", "institution_name")


class CommunicationLogInline(admin.TabularInline):
    model = CommunicationLog
    extra = 0
    readonly_fields = ("recipient_name", "recipient_email", "status", "error_message", "sent_at", "created_at")
    fields = ("recipient_name", "recipient_email", "status", "error_message", "sent_at", "created_at")
    can_delete = False


@admin.register(CommunicationBatch)
class CommunicationBatchAdmin(admin.ModelAdmin):
    list_display = ("name", "communication_type", "status", "send_mode", "test_recipient", "created_by", "created_at", "sent_at")
    list_filter = ("communication_type", "status", "send_mode", "dry_run")
    search_fields = ("name",)
    readonly_fields = ("created_at", "updated_at", "sent_at")
    inlines = [CommunicationLogInline]


@admin.register(CommunicationLog)
class CommunicationLogAdmin(admin.ModelAdmin):
    list_display = (
        "recipient_name",
        "original_recipient_email",
        "physical_recipient_email",
        "communication_type",
        "status",
        "created_at",
        "sent_at",
    )
    list_filter = ("communication_type", "status")
    search_fields = ("recipient_name", "recipient_email", "subject", "error_message")
    readonly_fields = ("created_at", "updated_at")
