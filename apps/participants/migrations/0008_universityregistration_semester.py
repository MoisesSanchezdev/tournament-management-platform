import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("participants", "0007_registration_attendance_workflow"),
    ]

    operations = [
        migrations.AddField(
            model_name="universityregistration",
            name="semester",
            field=models.PositiveSmallIntegerField(
                default=1,
                help_text="Semestre actual del equipo universitario. Solo participan estudiantes hasta cuarto semestre.",
                validators=[
                    django.core.validators.MinValueValidator(1),
                    django.core.validators.MaxValueValidator(4),
                ],
            ),
        ),
    ]
