from django.db import models

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
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES)
    disponible = models.BooleanField(default=True)
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)

    def __str__(self):
        return f"{self.nombre_producto} ({self.precio} Bs.)"