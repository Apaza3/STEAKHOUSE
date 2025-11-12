# ...existing code...
from django.db import models

# Conservamos la clase para tipos de cliente (compatibilidad con cambios entrantes)
class ClientesTipo(models.Model):
    tipo_cliente = models.CharField(max_length=50)

    def __str__(self):
        return self.tipo_cliente

# Mantengo principalmente tu modelo Cliente (nombre/apellido/ci_nit)
# pero añado campos opcionales compatibles con los cambios entrantes
class Cliente(models.Model):
    # FK opcional para compatibilidad con la nueva tabla de tipos
    cliente_tipo = models.ForeignKey(ClientesTipo, on_delete=models.SET_NULL, null=True, blank=True)

    # Campos originales tuyos
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    ci_nit = models.CharField(max_length=20, unique=True)

    # Campos añadidos por compatibilidad (opcional, no rompen tu esquema)
    nombre_cliente = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(max_length=100, unique=True, blank=True, null=True)
    telefono = models.CharField(max_length=50, blank=True, null=True)
    fecha_registro = models.DateField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        # Preferimos mostrar "Nombre Apellido" si existe; si no, fallback a nombre_cliente
        if self.nombre or self.apellido:
            return f"{self.nombre} {self.apellido}".strip()
        return self.nombre_cliente or f"Cliente {self.pk}"

# Conservamos la tabla de dispositivos de los compañeros
class ClientesDispositivos(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='dispositivos')
    num_dispos = models.CharField(max_length=50, help_text="ID de dispositivo para notificaciones")

    def __str__(self):
        # Usamos nombre + apellido si disponible, sino nombre_cliente
        cliente_nombre = str(self.cliente)
        return f"Dispositivo de {cliente_nombre}"
# ...existing code...