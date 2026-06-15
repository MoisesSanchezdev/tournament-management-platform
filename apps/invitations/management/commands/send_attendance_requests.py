from django.core.management.base import BaseCommand
from apps.participants.models import SchoolRegistration, UniversityRegistration, RegistrationStatus
from apps.participants.services import send_attendance_confirmation_request_email


class Command(BaseCommand):
    help = 'Envía correos de confirmación de asistencia a registros pendientes'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true')
        parser.add_argument('--base-url', type=str,
                            default='https://explotaglobos.com',
                            help='URL base del sitio')

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        base_url = options['base_url'].rstrip('/')

        enviados = 0
        errores = 0

        grupos = [
            (SchoolRegistration, 'colegio'),
            (UniversityRegistration, 'universidad'),
        ]

        for Model, tipo in grupos:
            registros = Model.objects.filter(
                status=RegistrationStatus.SUBMITTED,
                attendance_confirmed_at__isnull=True,
            )

            self.stdout.write(f'\n{tipo.capitalize()}s pendientes: {registros.count()}')

            for reg in registros:
                confirmation_url = f"{base_url}/registro/confirmar-asistencia/{reg.attendance_token}/"

                if dry_run:
                    self.stdout.write(
                        f'  [DRY-RUN] {reg.institution_name} - {reg.robot_name} → {reg.contact_email}'
                    )
                else:
                    try:
                        send_attendance_confirmation_request_email(reg, tipo, confirmation_url)
                        self.stdout.write(self.style.SUCCESS(
                            f'  ✓ {reg.institution_name} - {reg.robot_name} → {reg.contact_email}'
                        ))
                        enviados += 1
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(
                            f'  ✗ Error con {reg.institution_name}: {e}'
                        ))
                        errores += 1

        self.stdout.write(f'\nTotal enviados: {enviados} | Errores: {errores}')