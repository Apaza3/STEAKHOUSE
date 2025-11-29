from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

# Importamos los modelos de TUS apps
from pedidos.models import Pedido
from reservas.models import Reserva
from productos.models import Producto

# Importamos los modelos de AUDITORÍA
from .models import AuditoriaVenta, AuditoriaReserva, AuditoriaProducto

# --- SEÑALES PARA PEDIDOS (VENTAS) ---
@receiver(post_save, sender=Pedido)
def auditar_pedido_save(sender, instance, created, **kwargs):
    accion = 'CREACION' if created else 'ACTUALIZACION'
    
    # Intentamos obtener un nombre de usuario responsable
    responsable = "Sistema"
    if instance.usuario:
        responsable = instance.usuario.username
    elif instance.cliente:
        responsable = f"Cliente: {instance.cliente.nombre} {instance.cliente.apellido}"

    AuditoriaVenta.objects.create(
        usuario_responsable=responsable,
        accion=accion,
        id_pedido_original=str(instance.id),
        total_venta=instance.total,
        estado_venta=instance.estado_pedido,
        detalles=f"Pedido para Mesa: {instance.mesa}" if instance.mesa else "Pedido para llevar/delivery"
    )

# --- SEÑALES PARA RESERVAS ---
@receiver(post_save, sender=Reserva)
def auditar_reserva_save(sender, instance, created, **kwargs):
    accion = 'CREACION' if created else 'ACTUALIZACION'
    
    nombre_cliente = "Desconocido"
    if instance.cliente:
        nombre_cliente = f"{instance.cliente.nombre} {instance.cliente.apellido}"

    AuditoriaReserva.objects.create(
        usuario_cliente=nombre_cliente,
        accion=accion,
        id_reserva_original=str(instance.id),
        fecha_reserva=instance.fecha_reserva,
        hora_reserva=instance.hora_reserva,
        numero_personas=instance.numero_personas
    )

# --- SEÑALES PARA PRODUCTOS ---
@receiver(post_save, sender=Producto)
def auditar_producto_save(sender, instance, created, **kwargs):
    accion = 'CREACION' if created else 'MODIFICACION'
    
    AuditoriaProducto.objects.create(
        accion=accion,
        nombre_producto=instance.nombre_producto,
        precio_registrado=instance.precio,
        categoria=instance.categoria
    )