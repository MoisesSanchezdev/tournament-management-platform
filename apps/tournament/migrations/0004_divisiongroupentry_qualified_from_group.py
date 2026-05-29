from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tournament", "0003_divisioncompetition_configuration_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="divisiongroupentry",
            name="qualified_from_group",
            field=models.BooleanField(default=False),
        ),
    ]
