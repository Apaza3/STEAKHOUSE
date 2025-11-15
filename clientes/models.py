from django.db import models
from django.contrib.auth.models import User

class Cliente(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name="cliente")
    
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    # ===============================================
    # ¡NUEVO! Campo para Foto de Perfil (Opcional)
    # ===============================================
    # 'upload_to' guardará las fotos en 'media/perfiles/'
    foto_perfil = models.ImageField(upload_to='perfiles/', null=True, blank=True)
    # ===============================================

    def __str__(self):
        return f"{self.nombre} {self.apellido}"