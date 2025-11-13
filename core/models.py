from django.db import models

class Mesa(models.Model):
    ESTADO_CHOICES = (
        ('DISPONIBLE', 'Disponible'),
        ('OCUPADA', 'Ocupada'),
        ('RESERVADA', 'Reservada'),
        ('MANTENIMIENTO', 'Mantenimiento'),
    )
    
    numero = models.IntegerField(unique=True, help_text="Número de la mesa")
    capacidad = models.IntegerField(help_text="Número de personas que puede sentar")
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='DISPONIBLE')

    def __str__(self):
        return f"Mesa {self.numero} (Capacidad: {self.capacidad})"