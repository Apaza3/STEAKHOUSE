from django.db import models
from core.models import Mesa
from clientes.models import Cliente
import uuid

class Reserva(models.Model):
    
    ESTADO_CHOICES = (
        ('PENDIENTE', 'Pendiente'),
        ('CONFIRMADA', 'Confirmada'),
        ('CANCELADA', 'Cancelada'),
        ('COMPLETADA', 'Completada'),
        ('NO_SHOW', 'No Show'),
    )
    
    TIPO_PAGO_CHOICES = (
        ('SOLO_MESA', 'Solo Mesa'),
        ('PAGO_ADELANTADO', 'Pago QR'),
        ('TARJETA', 'Tarjeta'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    
    # --- ¡LA CORRECCIÓN ESTÁ AQUÍ! ---
    # Le decimos a la BD que esta columna SÍ PUEDE estar vacía (null=True)
    # y que si se borra una mesa, ponga este campo en NULL.
    mesa = models.ForeignKey(Mesa, on_delete=models.SET_NULL, null=True, blank=True)
    # --- FIN DE LA CORRECCIÓN ---

    fecha_reserva = models.DateField()
    hora_reserva = models.TimeField()
    numero_personas = models.IntegerField()
    
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='PENDIENTE')
    tipo_pago = models.CharField(max_length=20, choices=TIPO_PAGO_CHOICES, default='SOLO_MESA')

    def __str__(self):
        return f'Reserva de {self.cliente.nombre} [{self.estado}]'