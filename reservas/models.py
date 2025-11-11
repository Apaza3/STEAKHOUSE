from django.db import models
from clientes.models import Cliente # Importamos del Módulo Clientes

# Reemplaza 'CREATE TABLE Estados_Reservas'
class EstadosReserva(models.Model):
    nombre_estado = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.nombre_estado

# Reemplaza 'CREATE TABLE Mesas'
class Mesa(models.Model):
    numero_mesas = models.IntegerField(unique=True)
    capacidad_mesas = models.IntegerField()
    estado_mesas = models.CharField(max_length=50, default='disponible')

    def __str__(self):
        return f"Mesa {self.numero_mesas} (Capacidad: {self.capacidad_mesas})"

# Reemplaza 'CREATE TABLE Reservas'
class Reserva(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True)
    estado_reserva = models.ForeignKey(EstadosReserva, on_delete=models.PROTECT)
    fecha_reserva = models.DateTimeField()
    
    # Reemplaza la tabla 'Reservas_Mesas'
    mesas = models.ManyToManyField(Mesa)
    
    def __str__(self):
        return f"Reserva de {self.cliente} para {self.fecha_reserva}"

# Reemplaza 'CREATE TABLE Politicas_Reservas'
class PoliticaReserva(models.Model):
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE)
    descripcion_politica = models.CharField(max_length=200)
    tiempo_min = models.IntegerField(help_text="Tiempo mínimo de antelación en horas")
    multa_cancelacion = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    def __str__(self):
        return f"Política para Reserva {self.reserva.id}"