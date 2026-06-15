from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="CommunicationTemplate",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=160)),
                (
                    "template_type",
                    models.CharField(
                        choices=[
                            ("colegio", "Colegio"),
                            ("universidad", "Universidad"),
                            ("patrocinador", "Patrocinador"),
                            ("asistencia", "Asistencia"),
                            ("general", "General"),
                        ],
                        max_length=24,
                    ),
                ),
                ("file", models.FileField(upload_to="communication_templates/")),
                ("required_markers", models.JSONField(blank=True, default=list)),
                ("description", models.TextField(blank=True)),
                ("is_active", models.BooleanField(default=False)),
                ("validation_errors", models.JSONField(blank=True, default=list)),
            ],
            options={
                "ordering": ["template_type", "-is_active", "name"],
            },
        ),
        migrations.CreateModel(
            name="CommunicationRecipient",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=180)),
                ("email", models.EmailField(max_length=254)),
                (
                    "recipient_type",
                    models.CharField(
                        choices=[
                            ("colegio", "Colegio"),
                            ("universidad", "Universidad"),
                            ("patrocinador", "Patrocinador"),
                            ("asistencia", "Asistencia"),
                            ("general", "General"),
                        ],
                        max_length=24,
                    ),
                ),
                ("institution_name", models.CharField(blank=True, max_length=180)),
                ("extra_data", models.JSONField(blank=True, default=dict)),
            ],
            options={
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="CommunicationBatch",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=180)),
                (
                    "communication_type",
                    models.CharField(
                        choices=[
                            ("colegio", "Colegio"),
                            ("universidad", "Universidad"),
                            ("patrocinador", "Patrocinador"),
                            ("asistencia", "Asistencia"),
                            ("general", "General"),
                        ],
                        max_length=24,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("draft", "Borrador"),
                            ("previewed", "Previsualizado"),
                            ("sending", "En envio"),
                            ("sent", "Enviado"),
                            ("failed", "Fallido"),
                            ("cancelled", "Cancelado"),
                        ],
                        default="draft",
                        max_length=24,
                    ),
                ),
                ("dry_run", models.BooleanField(default=True)),
                ("sent_at", models.DateTimeField(blank=True, null=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="communication_batches",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "template",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="batches",
                        to="invitations.communicationtemplate",
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="CommunicationLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("recipient_name", models.CharField(max_length=180)),
                ("recipient_email", models.EmailField(blank=True, max_length=254)),
                (
                    "communication_type",
                    models.CharField(
                        choices=[
                            ("colegio", "Colegio"),
                            ("universidad", "Universidad"),
                            ("patrocinador", "Patrocinador"),
                            ("asistencia", "Asistencia"),
                            ("general", "General"),
                        ],
                        max_length=24,
                    ),
                ),
                ("subject", models.CharField(blank=True, max_length=220)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pendiente"),
                            ("sent", "Enviado"),
                            ("skipped", "Omitido"),
                            ("failed", "Fallido"),
                            ("dry_run", "Simulado"),
                        ],
                        default="pending",
                        max_length=24,
                    ),
                ),
                ("error_message", models.TextField(blank=True)),
                ("rendered_preview", models.TextField(blank=True)),
                ("sent_at", models.DateTimeField(blank=True, null=True)),
                (
                    "batch",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="logs",
                        to="invitations.communicationbatch",
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="communicationtemplate",
            index=models.Index(fields=["template_type", "is_active"], name="invitations_templat_5b38c8_idx"),
        ),
        migrations.AddIndex(
            model_name="communicationrecipient",
            index=models.Index(fields=["recipient_type"], name="invitations_recipie_0c344d_idx"),
        ),
        migrations.AddIndex(
            model_name="communicationrecipient",
            index=models.Index(fields=["email"], name="invitations_email_c11295_idx"),
        ),
        migrations.AddIndex(
            model_name="communicationbatch",
            index=models.Index(fields=["communication_type", "status"], name="invitations_communi_2bda52_idx"),
        ),
        migrations.AddIndex(
            model_name="communicationbatch",
            index=models.Index(fields=["created_at"], name="invitations_created_5a07d9_idx"),
        ),
        migrations.AddIndex(
            model_name="communicationlog",
            index=models.Index(fields=["communication_type", "status"], name="invitations_communi_bf7742_idx"),
        ),
        migrations.AddIndex(
            model_name="communicationlog",
            index=models.Index(fields=["recipient_email"], name="invitations_recipie_c3d21b_idx"),
        ),
        migrations.AddIndex(
            model_name="communicationlog",
            index=models.Index(fields=["created_at"], name="invitations_created_3a4704_idx"),
        ),
    ]
