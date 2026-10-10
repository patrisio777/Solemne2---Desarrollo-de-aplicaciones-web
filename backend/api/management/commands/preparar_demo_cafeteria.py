from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db import transaction


class Command(BaseCommand):
    help = 'Actualiza las seis cuentas ficticias del panel local de la cafetería.'

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError('Los usuarios de demostración solo se preparan en desarrollo.')
        # Reutiliza las cuentas de la primera vista previa para conservar la sesión.
        filas = [
            ('vista_admin', 'Cristobal', 'Garrido', 'cristobal.garrido@example.com', True),
            ('vista_admin_2', 'Patricio', 'Chaung', 'patricio.chaung@example.com', True),
            ('vista_cliente_1', 'Gabriel', 'Moreno', 'gabriel.moreno@example.com', False),
            ('vista_cliente_2', 'Brandon', 'Valdés', 'brandon.valdes@example.com', False),
            ('vista_cliente_3', 'Javiera', 'Fuentealba', 'javiera.fuentealba@example.com', False),
            ('vista_cliente_4', 'Jose', 'Arguello', 'jose.arguello@example.com', False),
        ]
        User = get_user_model()
        with transaction.atomic():
            for username, nombre, apellido, correo, admin in filas:
                usuario, creado = User.objects.get_or_create(username=username)
                usuario.first_name = nombre
                usuario.last_name = apellido
                usuario.email = correo
                usuario.is_staff = admin
                usuario.is_superuser = False
                if creado:
                    usuario.set_unusable_password()
                usuario.save()
        self.stdout.write(self.style.SUCCESS('Demo preparada: 2 administradores y 4 clientes.'))
