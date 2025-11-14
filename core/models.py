from django.db import models

class Mesa(models.Model):
    ESTADO_CHOICES = (
        ('DISPONIBLE', 'Disponible'),
        ('OCUPADA', 'Ocupada'),
        ('RESERVADA', 'Reservada'),
        ('MANTENIMIENTO', 'Mantenimiento'),
    )
    
    # --- ¡NUEVO! Campo TIPO (Normal/Premium) ---
    TIPO_CHOICES = (
        ('NORMAL', 'Normal'),
        ('PREMIUM', 'Premium (Ventana/Privado)'),
    )
    # --- Fin del campo nuevo ---

    numero = models.IntegerField(unique=True, help_text="Número de la mesa")
    capacidad = models.IntegerField(help_text="Número de personas que puede sentar")
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='DISPONIBLE')
    
    # --- ¡NUEVO! Campo TIPO añadido ---
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, default='NORMAL')

    def __str__(self):
        # Actualizamos el string para incluir el tipo
        return f"Mesa {self.numero} ({self.get_tipo_display()}) - Capacidad: {self.capacidad}"