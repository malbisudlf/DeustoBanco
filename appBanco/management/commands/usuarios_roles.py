from django.contrib.auth.models import Group, User
from django.core.management.base import BaseCommand
from django.db import transaction

USUARIOS_ROLES = (
    ('consulta', 'Consulta de movimientos'),
    ('editor', 'Edición de movimientos'),
)


class Command(BaseCommand):
    help = 'Crea (o actualiza) los usuarios consulta y editor con sus roles de movimientos.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--password',
            required=True,
            help='Contraseña que se asigna a los dos usuarios de prueba.',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        for nombre, grupo in USUARIOS_ROLES:
            usuario, _ = User.objects.get_or_create(username=nombre)
            usuario.is_staff = True
            usuario.set_password(options['password'])
            usuario.save()
            usuario.groups.set([Group.objects.get(name=grupo)])
            self.stdout.write(self.style.SUCCESS(f'Usuario {nombre} listo con el rol «{grupo}».'))
