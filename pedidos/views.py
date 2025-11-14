from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Producto, Pedido, DetallePedido
from clientes.models import Cliente

# ===============================================
# VISTA DEL MENÚ (Protegida)
# ===============================================
@login_required(login_url='login') # ¡PROTEGIDA!
def menu_view(request):
    productos = Producto.objects.filter(disponible=True)
    
    # Lógica del carrito (para el modal)
    carrito_session = request.session.get('carrito', {})
    items_del_carrito = []
    total_del_carrito = 0

    for producto_id, item in carrito_session.items():
        subtotal = item['cantidad'] * item['precio']
        items_del_carrito.append({
            'producto_id': producto_id,
            'nombre': item['nombre'],
            'cantidad': item['cantidad'],
            'precio': item['precio'],
            'subtotal': subtotal
        })
        total_del_carrito += subtotal
    
    context = {
        'productos': productos,
        'items_del_carrito': items_del_carrito,
        'total_del_carrito': total_del_carrito
    }
    return render(request, 'menu.html', context)

# ===============================================
# VISTA PARA AÑADIR AL CARRITO
# ===============================================
@login_required(login_url='login') # ¡PROTEGIDA!
def agregar_al_carrito_view(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    carrito = request.session.get('carrito', {})
    producto_id_str = str(producto.id)
    
    if producto_id_str in carrito:
        carrito[producto_id_str]['cantidad'] += 1
    else:
        carrito[producto_id_str] = {'cantidad': 1, 'precio': float(producto.precio), 'nombre': producto.nombre_producto}
    
    request.session['carrito'] = carrito
    messages.success(request, f"'{producto.nombre_producto}' añadido al carrito.")
    
    return redirect('menu_page')

# ===============================================
# VISTA PARA VER EL CARRITO (Simplificada)
# ===============================================
@login_required(login_url='login') # ¡PROTEGIDA!
def ver_carrito_view(request):
    # Esta vista ahora solo redirige al menú.
    # El carrito se mostrará en un modal en la misma página del menú.
    return redirect('menu_page')

# ===============================================
# VISTA PARA CONFIRMAR EL PEDIDO (¡CORREGIDA!)
# ===============================================
@login_required(login_url='login') 
def confirmar_pedido_view(request):
    carrito = request.session.get('carrito', {})
    if not carrito:
        messages.error(request, 'Tu carrito está vacío.')
        return redirect('menu_page')

    # --- ¡ESTE ES EL ARREGLO DEL CRASH! ---
    try:
        # Ahora sí podemos buscar 'request.user.cliente'
        # porque el modelo Cliente TIENE el campo 'usuario'.
        cliente_actual = request.user.cliente 
    except Cliente.DoesNotExist:
        # Si falla (ej. es 'potasio'), no enlazamos cliente.
        cliente_actual = None 
    # --- FIN DEL ARREGLO ---

    # 1. Crear el Pedido
    nuevo_pedido = Pedido.objects.create(
        usuario=request.user,  # El User logueado
        cliente=cliente_actual, # El Cliente enlazado (si existe)
        estado_pedido='EN_PREPARACION', # Como es pago en restaurante, entra a preparación
        total = 0 # El total se calculará ahora
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
# VISTA DE ÉXITO
# ===============================================
@login_required(login_url='login')
def pedido_exitoso_view(request):
    return render(request, 'pedido_exitoso.html')