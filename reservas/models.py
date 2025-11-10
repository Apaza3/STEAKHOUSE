import uuid
from django.db import models
from django.conf import settings # Para enlazar con el usuario de Django

# ===============================================
# MODELO PARA TU "TABLA_MESA" 
# ===============================================
class Mesa(models.Model):
    ESTADO_MESA_CHOICES = (
        ('DISPONIBLE', 'Disponible'),
        ('OCUPADA', 'Ocupada'),
        ('RESERVADA', 'Reservada'),
    )
    
    # Usamos el Id automático de Django (PK)
    nro_mesa = models.PositiveIntegerField(unique=True) # [cite: 32]
    capacidad = models.PositiveIntegerField() # [cite: 33]
    estado_mesa = models.CharField(max_length=20, choices=ESTADO_MESA_CHOICES, default='DISPONIBLE') # [cite: 34]

    def __str__(self):
        return f"Mesa {self.nro_mesa} (Capacidad: {self.capacidad})"

# ===============================================
# MODELO PARA TU "TABLA_RESERVA" 
# ===============================================
class Reserva(models.Model):
    ESTADO_RESERVA_CHOICES = (
        ('PENDIENTE', 'Pendiente'),
        ('CONFIRMADA', 'Confirmada'),
        ('CANCELADA', 'Cancelada'),
        ('COMPLETADA', 'Completada'),
    )
    ESTADO_PAGO_CHOICES = (
        ('PENDIENTE', 'Pendiente'),
        ('PAGADO', 'Pagado'),
        ('REEMBOLSADO', 'Reembolsado'),
    )
    TIPO_RESERVA_CHOICES = (
        ('MESA', 'Solo Mesa'),
        ('PAGO', 'Pago Adelantado'),
    )

    # Este es el ID único (ej. RESERVA-ABC-123) que usaremos en la URL del QR
    # Lo usamos como Primary Key (PK) [cite: 21]
    id_reserva = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Claves Foráneas (FK) de tu PDF
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True) # 
    mesa = models.ForeignKey(Mesa, on_delete=models.SET_NULL, null=True, blank=True) # 

    # Datos de la reserva
    fecha = models.DateField() # [cite: 23]
    hora = models.TimeField() # [cite: 24]
    cant_personas = models.PositiveIntegerField() # [cite: 25]
    
    # Datos del cliente (si no está logueado)
    nombre_cliente = models.CharField(max_length=100, null=True, blank=True)
    email_cliente = models.EmailField(null=True, blank=True)
    
    # Estados para la simulación
    estado_reserva = models.CharField(max_length=20, choices=ESTADO_RESERVA_CHOICES, default='PENDIENTE') # [cite: 27]
    estado_pago = models.CharField(max_length=20, choices=ESTADO_PAGO_CHOICES, default='PENDIENTE') # 
    tipo_reserva = models.CharField(max_length=10, choices=TIPO_RESERVA_CHOICES, default='MESA') # 

    creada_en = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        # Mostramos el nombre del usuario logueado o el nombre del cliente invitado
        nombre = self.usuario.username if self.usuario else self.nombre_cliente
        return f"Reserva de {nombre} para el {self.fecha}"