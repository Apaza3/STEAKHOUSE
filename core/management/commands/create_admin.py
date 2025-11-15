import os
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()

class Command(BaseCommand):
    help = "Crea un superusuario si no existe, usando variables de entorno."

    def handle(self, *args, **options):
        # Lee las variables de entorno de Render
        username = os.environ.get('ADMIN_USER')
        password = os.environ.get('ADMIN_PASS')
        email = os.environ.get('ADMIN_EMAIL')

        # Comprueba si tenemos todos los datos
        if not all([username, password, email]):
            self.stdout.write(self.style.ERROR(
                'Faltan variables de entorno (ADMIN_USER, ADMIN_PASS, ADMIN_EMAIL). No se pudo crear el admin.'
            ))
            return

        # Lógica para crear el admin SOLO SI NO EXISTE
        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            self.stdout.write(self.style.SUCCESS(
                f"Superusuario '{username}' creado exitosamente."
            ))
        else:
            self.stdout.write(self.style.WARNING(
                f"El superusuario '{username}' ya existe. No se hizo nada."
            ))