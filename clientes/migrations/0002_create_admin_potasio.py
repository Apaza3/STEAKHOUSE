from django.db import migrations
from django.contrib.auth.models import User

def create_admin_user(apps, schema_editor):
    """
    Crea nuestro superusuario 'potasio' con la contraseña '4852'
    solo si no existe ya.
    """
    if not User.objects.filter(username='potasio').exists():
        print("\nCreando superusuario 'potasio'...")
        User.objects.create_superuser(
            username='potasio',
            email='potasio@admin.com',
            password='48524852'
        )
    else:
        print("\nEl usuario 'potasio' ya existe.")

class Migration(migrations.Migration):

    dependencies = [
        ('clientes', '0001_initial'), # Depende de la migración inicial de clientes
    ]

    operations = [
        # Ejecuta nuestra función de Python durante la migración
        migrations.RunPython(create_admin_user),
    ]