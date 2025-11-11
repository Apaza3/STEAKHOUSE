from django.db import models
from clientes.models import Cliente
from reservas.models import Mesa # Reutilizamos 'Mesa' de la app 'reservas'

# Reemplaza 'CREATE TABLE Estados_Pedidos'
class EstadosPedido(models.Model):
    nombre_estado = models.CharField(max_length=50) # Ej: "Recibido", "En preparación", "Servido"
    descripcion = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.nombre_estado

# Reemplaza 'CREATE TABLE Pedidos'
class Pedido(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True)
    mesa = models.ForeignKey(Mesa, on_delete=models.SET_NULL, null=True)
    estado = models.ForeignKey(EstadosPedido, on_delete=models.PROTECT)
    fecha_pedido = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pedido {self.id} de {self.cliente.nombre_cliente}"