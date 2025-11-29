from django.contrib import admin
from .models import AuditoriaVenta, AuditoriaReserva, AuditoriaProducto

@admin.register(AuditoriaVenta)
class AuditoriaVentaAdmin(admin.ModelAdmin):
    list_display = ('fecha_accion', 'accion', 'usuario_responsable', 'total_venta', 'estado_venta')
    list_filter = ('accion', 'fecha_accion')
    search_fields = ('id_pedido_original', 'usuario_responsable')

@admin.register(AuditoriaReserva)
class AuditoriaReservaAdmin(admin.ModelAdmin):
    list_display = ('fecha_accion', 'accion', 'usuario_cliente', 'fecha_reserva', 'numero_personas')
    list_filter = ('accion',)

@admin.register(AuditoriaProducto)
class AuditoriaProductoAdmin(admin.ModelAdmin):
    list_display = ('fecha_accion', 'accion', 'nombre_producto', 'precio_registrado', 'categoria')
    list_filter = ('accion', 'categoria')