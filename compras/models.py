from django.db import models
from productos.models import Producto # Importamos del Módulo Productos

# Reemplaza 'CREATE TABLE Proveedor'
class Proveedor(models.Model):
    nombre_prov = models.CharField(max_length=100)
    telefono_prov = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(max_length=100, blank=True, null=True)
    direccion_prov = models.CharField(max_length=200, blank=True, null=True)
    estado_prov = models.CharField(max_length=20, default='activo')

    def __str__(self):
        return self.nombre_prov

# Reemplaza 'CREATE TABLE Producto_Proveedor'
class ProductoProveedor(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)
    precio_compra = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('producto', 'proveedor')

    def __str__(self):
        return f"{self.producto.nombre_prod} - {self.proveedor.nombre_prov}"

# Reemplaza 'CREATE TABLE Estados_Compra'
class EstadosCompra(models.Model):
    nombre_estado = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.nombre_estado

# Reemplaza 'CREATE TABLE Compras'
class Compra(models.Model):
    proveedor = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, null=True)
    estado_compra = models.ForeignKey(EstadosCompra, on_delete=models.PROTECT)
    fecha_compra = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return f"Compra {self.id} a {self.proveedor.nombre_prov}"

# Reemplaza 'CREATE TABLE Detalle_Compras'
class DetalleCompra(models.Model):
    compra = models.ForeignKey(Compra, related_name='detalles', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad_compra = models.IntegerField()
    detalle_compra = models.CharField(max_length=200, blank=True, null=True)
    total_compra = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"Detalle {self.id} de Compra {self.compra.id}"