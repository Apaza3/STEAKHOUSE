from django.db import models
from django.contrib.auth.models import User

# Este es el modelo 'Cliente' que tu formulario de registro (ClienteRegistrationForm)
# espera. Enlaza el login (User) con los datos del cliente (Cliente).
class Cliente(models.Model):
    # ¡LA LÍNEA QUE FALTA!
    # Esto conecta un Cliente (tus datos) a un User (el login/pass de Django)
    # on_delete=models.CASCADE significa que si borras el User, se borra el Cliente.
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name="cliente")
    
    # Tus campos existentes (basados en el error)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    # (Omito los otros campos del error como ci_nit, cliente_tipo, etc.
    # por simplicidad. Los podemos añadir después si son necesarios
    # para el formulario de registro.)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"