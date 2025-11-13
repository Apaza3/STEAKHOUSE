from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Producto, Pedido, DetallePedido
from clientes.models import Cliente

# ===============================================
# VISTA DEL MENÚ (CORREGIDA)
# ===============================================
@login_required(login_url='login') 
def menu_view(request):
    productos = Producto.objects.filter(disponible=True)
    
    # --- ¡NUEVA LÓGICA DE CÁLCULO! ---
    # Hacemos los cálculos aquí, no en el template.
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
            'subtotal': subtotal  # Pasamos el subtotal ya calculado
        })
        total_del_carrito += subtotal
    # --- FIN DE LA LÓGICA ---
    
    context = {
        'productos': productos,
        'items_del_carrito': items_del_carrito, # Usamos la lista calculada
        'total_del_carrito': total_del_carrito  # Usamos el total calculado
    }
    return render(request, 'menu.html', context)

# ===============================================
# VISTA PARA AÑADIR AL CARRITO
# ===============================================
@login_required(login_url='login')
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
@login_required(login_url='login')
def ver_carrito_view(request):
    # Redirige de nuevo al menú, donde se muestra el modal
    return redirect('menu_page')

# ===============================================
# VISTA PARA CONFIRMAR EL PEDIDO (CORREGIDA)
# ===============================================
@login_required(login_url='login') 
def confirmar_pedido_view(request):
    carrito = request.session.get('carrito', {})
    if not carrito:
        messages.error(request, 'Tu carrito está vacío.')
        return redirect('menu_page')

    # --- ¡ARREGLO DEL AttributeError! ---
    try:
        cliente_actual = request.user.cliente 
    except Cliente.DoesNotExist:
        cliente_actual = None 
    # --- FIN DEL ARREGLO ---

    # 1. Crear el Pedido
    nuevo_pedido = Pedido.objects.create(
        usuario=request.user,
        cliente=cliente_actual,
        estado_pedido='EN_PREPARACION',
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