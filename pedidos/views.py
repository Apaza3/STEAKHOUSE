from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Pedido, DetallePedido
from clientes.models import Cliente
from productos.models import Producto # <-- ¡CORRECCIÓN! Importado desde 'productos'
from collections import defaultdict # <-- ¡NUEVO! Para agrupar

# ===============================================
# VISTA DEL MENÚ (Actualizada para agrupar)
# ===============================================
@login_required(login_url='login')
def menu_view(request):
    
    # Obtenemos todos los productos y los preparamos para agrupar
    productos = Producto.objects.filter(disponible=True).order_by('categoria')
    
    # ¡CAMBIO! Agrupamos los productos por su categoría
    productos_agrupados = defaultdict(list)
    for producto in productos:
        # Usamos get_categoria_display() para obtener el texto legible (ej. "Cortes de Carne")
        productos_agrupados[producto.get_categoria_display()].append(producto)
    
    # Convertimos el defaultdict a un dict normal para el template
    productos_agrupados = dict(productos_agrupados)
    
    # Lógica del carrito (para el modal) - Sin cambios
    carrito_session = request.session.get('carrito', {})
    items_del_carrito = []
    total_del_carrito = 0

    for producto_id, item in carrito_session.items():
        # Convertimos el precio a Decimal para evitar errores de formato
        precio = float(item['precio'])
        cantidad = item['cantidad']
        subtotal = cantidad * precio
        items_del_carrito.append({
            'producto_id': producto_id,
            'nombre': item['nombre'],
            'cantidad': cantidad,
            'precio': precio,
            'subtotal': subtotal
        })
        total_del_carrito += subtotal
    
    context = {
        # ¡CAMBIO! Enviamos los productos agrupados
        'productos_agrupados': productos_agrupados,
        'items_del_carrito': items_del_carrito,
        'total_del_carrito': total_del_carrito
    }
    # ¡CAMBIO! Usamos una plantilla namespaced
    return render(request, 'pedidos/menu.html', context)


# ===============================================
# VISTA PARA AÑADIR AL CARRITO (Corregida)
# ===============================================
@login_required(login_url='login')
def agregar_al_carrito_view(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    carrito = request.session.get('carrito', {})
    producto_id_str = str(producto.id)
    
    if producto_id_str in carrito:
        carrito[producto_id_str]['cantidad'] += 1
    else:
        # Guardamos el precio como string para evitar problemas de serialización JSON
        carrito[producto_id_str] = {'cantidad': 1, 'precio': str(producto.precio), 'nombre': producto.nombre_producto}
    
    request.session['carrito'] = carrito
    messages.success(request, f"'{producto.nombre_producto}' añadido al carrito.")
    
    # Redirige de vuelta a la página del menú
    return redirect('menu_page')

# ===============================================
# VISTA PARA VER EL CARRITO (Simplificada)
# ===============================================
@login_required(login_url='login')
def ver_carrito_view(request):
    # Esta vista ahora solo redirige al menú.
    return redirect('menu_page')

# ===============================================
# VISTA PARA CONFIRMAR EL PEDIDO (Corregida)
# ===============================================
@login_required(login_url='login') 
def confirmar_pedido_view(request):
    carrito = request.session.get('carrito', {})
    if not carrito:
        messages.error(request, 'Tu carrito está vacío.')
        return redirect('menu_page')

    try:
        cliente_actual = request.user.cliente 
    except Cliente.DoesNotExist:
        # Si falla (ej. es 'potasio'), no enlazamos cliente.
        cliente_actual = None 
        messages.warning(request, 'Tu cuenta de admin no está enlazada a un perfil de cliente, el pedido se creará sin él.')

    # 1. Crear el Pedido
    nuevo_pedido = Pedido.objects.create(
        usuario=request.user,
        cliente=cliente_actual,
        estado_pedido='PENDIENTE', # ¡CAMBIO! Inicia como PENDIENTE para que el cajero lo vea
        total = 0
    )
    
    total_final = 0
    
    # 2. Crear los Detalles del Pedido
    for producto_id, item_data in carrito.items():
        producto = get_object_or_404(Producto, id=int(producto_id))
        cantidad = item_data['cantidad']
        
        detalle = DetallePedido.objects.create(
            pedido=nuevo_pedido,
            producto=producto,
            cantidad=cantidad
            # El precio_unitario y subtotal se calculan solos (ver models.py)
        )
        total_final += detalle.subtotal
    
    # 3. Actualizar el total
    nuevo_pedido.total = total_final
    nuevo_pedido.save()
    
    # 4. Limpiar el carrito
    del request.session['carrito']
    
    messages.success(request, '¡Pedido confirmado! Hemos recibido tu orden.')
    return redirect('pedido_exitoso')

# ===============================================
# VISTA DE ÉXITO (Corregida)
# ===============================================
@login_required(login_url='login')
def pedido_exitoso_view(request):
    # ¡CAMBIO! Usamos una plantilla namespaced
    return render(request, 'pedidos/pedido_exitoso.html')

# ===============================================
# ¡NUEVA! VISTA "MIS PEDIDOS"
# ===============================================
@login_required(login_url='login')
def mis_pedidos_view(request):
    # Buscamos todos los pedidos hechos por el usuario logueado
    pedidos = Pedido.objects.filter(usuario=request.user).order_by('-fecha_pedido')
    
    context = {
        'pedidos': pedidos
    }
    return render(request, 'pedidos/mis_pedidos.html', context)