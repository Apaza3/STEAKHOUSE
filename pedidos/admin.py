from django.contrib import admin
from .models import Producto, Pedido, DetallePedido

# Esto nos permite ver los detalles DENTRO de la pantalla del Pedido
class DetallePedidoInline(admin.TabularInline):
    model = DetallePedido
    extra = 1
    readonly_fields = ('subtotal',) # Para que no se pueda editar manualmente

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre_producto', 'categoria', 'precio', 'disponible')
    list_filter = ('categoria', 'disponible')
    search_fields = ('nombre_producto',)

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'mesa', 'usuario', 'fecha_pedido', 'estado_pedido', 'total')
    list_filter = ('estado_pedido', 'fecha_pedido')
    inlines = [DetallePedidoInline]
