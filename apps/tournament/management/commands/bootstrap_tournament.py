from django.core.management.base import BaseCommand

from apps.tournament.models import RuleSection, TournamentEdition


class Command(BaseCommand):
    help = "Crea una edicion inicial activa y reglas base para comenzar a trabajar."

    def handle(self, *args, **options):
        edition, created = TournamentEdition.objects.get_or_create(
            name="Edicion inicial de trabajo",
            defaults={
                "description": (
                    "Edicion base para configurar el proyecto mientras se define "
                    "el reglamento oficial del torneo."
                ),
                "location": "Universidad Tecnologica de Pereira",
                "is_active": True,
            },
        )

        if not created and not edition.is_active:
            edition.is_active = True
            edition.save(update_fields=["is_active"])

        default_rules = [
            (
                "Categoria de participacion",
                "Se distinguiran instituciones de colegio y universidad.",
                "Cada equipo debe estar asociado a una institucion y a la categoria operativa definida por la organizacion.",
            ),
            (
                "Condiciones del robot",
                "El robot debe cumplir las restricciones tecnicas publicadas por el torneo.",
                "Las especificaciones definitivas de peso, dimensiones, materiales y seguridad se cargaran en esta misma plataforma.",
            ),
            (
                "Formato competitivo",
                "Las fases del torneo podran ajustarse durante el diseno operativo.",
                "La plataforma quedo preparada para manejar clasificatorias, grupos, llaves eliminatorias y fases personalizadas.",
            ),
        ]

        created_rules = 0
        for order, (title, summary, body) in enumerate(default_rules, start=1):
            _, rule_created = RuleSection.objects.get_or_create(
                edition=edition,
                title=title,
                defaults={
                    "summary": summary,
                    "body": body,
                    "order": order,
                    "is_published": True,
                },
            )
            if rule_created:
                created_rules += 1

        self.stdout.write(self.style.SUCCESS(f"Edicion activa lista: {edition.name}"))
        self.stdout.write(self.style.SUCCESS(f"Reglas creadas: {created_rules}"))
