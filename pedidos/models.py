from django.db import models
from django.conf import settings

# ===============================================
# MODELO PARA TU "TABLA_PRODUCTO" (El Menú)
# ===============================================
class Producto(models.Model):
    CATEGORIA_CHOICES = (
        ('CARNE', 'Cortes de Carne'),
        ('HAMBURGUESA', 'Hamburguesas'),
        ('GUARNICION', 'Guarniciones'),
        ('BEBIDA', 'Bebidas'),
        ('POSTRE', 'Postres'),
    )
    
    nombre_producto = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2) # Ej: 150.50
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES)
    disponible = models.BooleanField(default=True) # Para activar/desactivar platos
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True) # Foto del plato

    def __str__(self):
        return f"{self.nombre_producto} ({self.precio} Bs.)"

# ===============================================
# MODELO PARA TU "TABLA_PEDIDO" (La Cabecera)
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
    # Usamos settings.AUTH_USER_MODEL para que funcione aunque la app 'usuarios' no esté lista
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='pedidos_clientes')
    
    # Usamos 'reservas.Mesa' como texto para evitar el error de importación circular
    mesa = models.ForeignKey('reservas.Mesa', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Datos del Pedido
    fecha_pedido = models.DateTimeField(auto_now_add=True) # Se guarda automático al crear
    estado_pedido = models.CharField(max_length=20, choices=ESTADO_PEDIDO_CHOICES, default='PENDIENTE')
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Pedido #{self.id} - Total: {self.total} Bs."

# ===============================================
# MODELO PARA TU "TABLA_DETALLE_PEDIDO" (Los Items)
# ===============================================
class DetallePedido(models.Model):
    # Relaciones (FK)
    pedido = models.ForeignKey(Pedido, related_name='detalles', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT) # PROTECT evita borrar un producto si ya se vendió
    
    # Datos del Detalle
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2) # Guardamos el precio al momento de la compra
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        # Calculamos automáticamente el subtotal antes de guardar
        self.subtotal = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.cantidad}x {self.producto.nombre_producto} en Pedido #{self.pedido.id}"