from django.db import models

# Reemplaza 'CREATE TABLE Producto'
class Producto(models.Model):
    nombre_prod = models.CharField(max_length=100)
    descripcion_prod = models.CharField(max_length=200, blank=True, null=True)
    precio_prod = models.DecimalField(max_digits=10, decimal_places=2)
    categoria_prod = models.CharField(max_length=50)
    estado_prod = models.CharField(max_length=20, default='disponible')
    cantidad_prod = models.IntegerField(default=0, help_text="Cantidad en inventario")

    def __str__(self):
        return self.nombre_prod

# Reemplaza 'CREATE TABLE Menu'
class Menu(models.Model):
    platillo_menu = models.CharField(max_length=100)
    tipo_menu = models.CharField(max_length=50)
    descripcion_menu = models.CharField(max_length=200, blank=True, null=True)
    estado_menu = models.CharField(max_length=20, default='disponible')
    precio_menu = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Reemplaza la tabla 'Menu_Productos'
    productos = models.ManyToManyField(Producto, blank=True, help_text="Ingredientes de este platillo")

    def __str__(self):
        return self.platillo_menu