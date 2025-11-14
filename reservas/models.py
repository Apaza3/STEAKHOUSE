from django.db import models
from core.models import Mesa
from clientes.models import Cliente
import uuid
from datetime import datetime, timedelta

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
    
    mesa = models.ForeignKey(Mesa, on_delete=models.SET_NULL, null=True, blank=True)

    fecha_reserva = models.DateField()
    hora_reserva = models.TimeField()
    numero_personas = models.IntegerField()
    
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='PENDIENTE')
    tipo_pago = models.CharField(max_length=20, choices=TIPO_PAGO_CHOICES, default='SOLO_MESA')

    # Campos de Lógica de Negocio
    duracion_horas = models.IntegerField(default=2, help_text="Duración de la reserva en horas")
    hora_fin = models.TimeField(null=True, blank=True, editable=False)
    monto_pagado = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    # ===================================================
    # ¡NUEVO CAMPO REQUERIDO!
    # ===================================================
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    # ===================================================

    def __str__(self):
        return f'Reserva de {self.cliente.nombre} [{self.estado}]'

    def save(self, *args, **kwargs):
        # Lógica para auto-calcular la hora de fin
        if self.hora_reserva and self.duracion_horas:
            inicio_dt = datetime.combine(datetime.today(), self.hora_reserva)
            fin_dt = inicio_dt + timedelta(hours=self.duracion_horas)
            self.hora_fin = fin_dt.time()
            
        super().save(*args, **kwargs)