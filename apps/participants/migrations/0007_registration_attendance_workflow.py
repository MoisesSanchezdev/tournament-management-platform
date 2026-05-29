import uuid

from django.db import migrations, models


def populate_attendance_tokens(apps, schema_editor):
    SchoolRegistration = apps.get_model("participants", "SchoolRegistration")
    UniversityRegistration = apps.get_model("participants", "UniversityRegistration")

    for model in (SchoolRegistration, UniversityRegistration):
        for registration in model.objects.filter(attendance_token__isnull=True):
            registration.attendance_token = uuid.uuid4()
            registration.save(update_fields=["attendance_token"])


class Migration(migrations.Migration):

    dependencies = [
        ("participants", "0006_schoolregistration_unique_school_robot_registration_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="schoolregistration",
            name="attendance_confirmed_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="schoolregistration",
            name="attendance_request_sent_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="schoolregistration",
            name="attendance_token",
            field=models.UUIDField(blank=True, editable=False, null=True),
        ),
        migrations.AddField(
            model_name="schoolregistration",
            name="receipt_email_sent_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="schoolregistration",
            name="team_synced_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="universityregistration",
            name="attendance_confirmed_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="universityregistration",
            name="attendance_request_sent_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="universityregistration",
            name="attendance_token",
            field=models.UUIDField(blank=True, editable=False, null=True),
        ),
        migrations.AddField(
            model_name="universityregistration",
            name="receipt_email_sent_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="universityregistration",
            name="team_synced_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.RunPython(populate_attendance_tokens, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="schoolregistration",
            name="attendance_token",
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
        migrations.AlterField(
            model_name="universityregistration",
            name="attendance_token",
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
    ]
