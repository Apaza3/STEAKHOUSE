from django.db import models
from django.conf import settings

# --- AUDITORÍA DE VENTAS (PEDIDOS) ---
class AuditoriaVenta(models.Model):
    ACCION_CHOICES = (('CREACION', 'Creación'), ('ACTUALIZACION', 'Actualización'), ('ELIMINACION', 'Eliminación'))

    fecha_accion = models.DateTimeField(auto_now_add=True)
    usuario_responsable = models.CharField(max_length=150, null=True, blank=True, help_text="Usuario que realizó la acción")
    accion = models.CharField(max_length=20, choices=ACCION_CHOICES)
    
    # Datos respaldados
    id_pedido_original = models.CharField(max_length=50)
    total_venta = models.DecimalField(max_digits=10, decimal_places=2)
    estado_venta = models.CharField(max_length=50)
    
    # Un campo de texto para guardar detalles extra si quieres
    detalles = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Auditoría Venta {self.id_pedido_original} - {self.accion}"

# --- AUDITORÍA DE RESERVAS ---
class AuditoriaReserva(models.Model):
    ACCION_CHOICES = (('CREACION', 'Creación'), ('ACTUALIZACION', 'Actualización'), ('CANCELACION', 'Cancelación'))

    fecha_accion = models.DateTimeField(auto_now_add=True)
    usuario_cliente = models.CharField(max_length=150, null=True, blank=True) # Nombre del cliente
    accion = models.CharField(max_length=20, choices=ACCION_CHOICES)
    
    # Datos respaldados
    id_reserva_original = models.CharField(max_length=100)
    fecha_reserva = models.DateField(null=True)
    hora_reserva = models.TimeField(null=True)
    numero_personas = models.IntegerField(default=0)
    
    def __str__(self):
        return f"Auditoría Reserva {self.id_reserva_original} - {self.accion}"

# --- AUDITORÍA DE PRODUCTOS ---
class AuditoriaProducto(models.Model):
    ACCION_CHOICES = (('CREACION', 'Nuevo Producto'), ('MODIFICACION', 'Cambio de Precio/Stock'), ('BAJA', 'Eliminado'))

    fecha_accion = models.DateTimeField(auto_now_add=True)
    accion = models.CharField(max_length=20, choices=ACCION_CHOICES)
    
    # Datos respaldados
    nombre_producto = models.CharField(max_length=100)
    precio_registrado = models.DecimalField(max_digits=10, decimal_places=2)
    categoria = models.CharField(max_length=50)
    
    def __str__(self):
        return f"Log Producto: {self.nombre_producto} ({self.accion})"