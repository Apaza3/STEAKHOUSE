from django.db import models
from django.conf import settings
from core.models import Mesa
from productos.models import Producto
from clientes.models import Cliente # <-- ¡IMPORTANTE!

# ===============================================
# MODELO "PEDIDO" (CORREGIDO)
# ===============================================
class Pedido(models.Model):
    ESTADO_PEDIDO_CHOICES = (
        ('PENDIENTE', 'Pendiente'),
        ('EN_PREPARACION', 'En Preparación'),
        ('LISTO', 'Listo para Servir'),
        ('ENTREGADO', 'Entregado'),
        ('CANCELADO', 'Cancelado'),
    )
    
    # Relaciones (FK)
    # El 'usuario' es QUIÉN HIZO EL PEDIDO (el login)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="pedidos")
    # El 'cliente' son LOS DATOS de facturación (si es un cliente registrado)
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, blank=True) 
    
    mesa = models.ForeignKey(Mesa, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Datos del Pedido
    fecha_pedido = models.DateTimeField(auto_now_add=True)
    estado_pedido = models.CharField(max_length=20, choices=ESTADO_PEDIDO_CHOICES, default='PENDIENTE')
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Pedido #{self.id} - Total: {self.total} Bs."

# ===============================================
# MODELO "DETALLEPEDIDO" (Con save() automático)
# ===============================================
class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, related_name='detalles', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT) 
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2) # Se guarda el precio al momento de la compra
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        # Asignamos el precio del producto automáticamente
        if not self.precio_unitario:
            self.precio_unitario = self.producto.precio
        self.subtotal = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.cantidad}x {self.producto.nombre_producto} en Pedido #{self.pedido.id}"