# ventas/models.py

from django.db import models
from django.conf import settings # Para enlazar al mesero (Usuario)

# --- Modelos de Producto (Los que ya tenías) ---

class CategoriaProducto(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Categoría de Producto"
        verbose_name_plural = "Categorías de Productos"

class Producto(models.Model):
    categoria = models.ForeignKey(CategoriaProducto, on_delete=models.SET_NULL, null=True, related_name='productos')
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, help_text="Descripción del producto")
    precio = models.DecimalField(max_digits=10, decimal_places=2, help_text="Precio de venta")
    disponible = models.BooleanField(default=True, help_text="Marcar si el producto está disponible")

    def __str__(self):
        return f"{self.nombre} - Bs {self.precio}" # <-- (Cambié $ por Bs)

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"


# --- NUEVOS MODELOS PARA REGISTROS Y REPORTES ---

class Mesa(models.Model):
    numero = models.IntegerField(unique=True, help_text="Número de la mesa")
    capacidad = models.IntegerField(default=4, help_text="Cuántas personas caben")

    def __str__(self):
        return f"Mesa {self.numero}"

class Pedido(models.Model):
    ESTADO_CHOICES = (
        ('pendiente', 'Pendiente'),
        ('pagado', 'Pagado'),
        ('cancelado', 'Cancelado'),
    )

    mesa = models.ForeignKey(Mesa, on_delete=models.SET_NULL, null=True, blank=True)
    mesero = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, help_text="Usuario que tomó el pedido")
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Total calculado de la venta")
    creado_en = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Pedido (Venta)"
        verbose_name_plural = "Pedidos (Ventas)"

    def __str__(self):
        return f"Pedido {self.id} - Mesa {self.mesa.numero} - {self.estado}"

class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, help_text="Producto vendido") 
    cantidad = models.PositiveIntegerField(default=1)
    # Guarda el precio al momento de la venta, por si el precio del producto cambia después
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2) 

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"

    def save(self, *args, **kwargs):
        # Auto-rellena el precio al momento de guardar
        if not self.precio_unitario:
            self.precio_unitario = self.producto.precio
        super().save(*args, **kwargs)

    def get_subtotal(self):
        return self.precio_unitario * self.cantidad