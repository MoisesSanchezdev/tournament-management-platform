from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("invitations", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="communicationbatch",
            name="send_mode",
            field=models.CharField(
                choices=[
                    ("dry_run", "Simulacion segura"),
                    ("test", "Prueba controlada"),
                    ("official", "Envio oficial"),
                ],
                default="dry_run",
                max_length=24,
            ),
        ),
        migrations.AddField(
            model_name="communicationbatch",
            name="test_recipient",
            field=models.EmailField(blank=True, max_length=254),
        ),
        migrations.AddField(
            model_name="communicationlog",
            name="original_recipient_email",
            field=models.EmailField(blank=True, max_length=254),
        ),
        migrations.AddField(
            model_name="communicationlog",
            name="physical_recipient_email",
            field=models.EmailField(blank=True, max_length=254),
        ),
        migrations.AlterField(
            model_name="communicationlog",
            name="status",
            field=models.CharField(
                choices=[
                    ("pending", "Pendiente"),
                    ("sent", "Enviado"),
                    ("test_sent", "Prueba enviada"),
                    ("skipped", "Omitido"),
                    ("failed", "Fallido"),
                    ("dry_run", "Simulado"),
                ],
                default="pending",
                max_length=24,
            ),
        ),
    ]
