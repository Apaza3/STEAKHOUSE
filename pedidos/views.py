from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Producto, Pedido, DetallePedido
from clientes.models import Cliente # Necesitamos esto para ligar el pedido

# ===============================================
# VISTA PARA MOSTRAR EL MENÚ
# ===============================================
def menu_view(request):
    productos = Producto.objects.filter(disponible=True)
    return render(request, 'menu.html', {'productos': productos})

# ===============================================
# VISTA PARA AÑADIR AL CARRITO (EN LA SESIÓN)
# ===============================================
def agregar_al_carrito_view(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    
    # Usamos la sesión de Django para guardar el carrito
    carrito = request.session.get('carrito', {})
    
    # Convertimos el ID a string porque la sesión usa JSON
    producto_id_str = str(producto.id)
    
    # Añadimos o incrementamos la cantidad
    if producto_id_str in carrito:
        carrito[producto_id_str]['cantidad'] += 1
    else:
        carrito[producto_id_str] = {'cantidad': 1, 'precio': float(producto.precio), 'nombre': producto.nombre_producto}
    
    request.session['carrito'] = carrito
    messages.success(request, f"'{producto.nombre_producto}' añadido al carrito.")
    
    return redirect('menu_page') # Vuelve a la página del menú

# ===============================================
# VISTA PARA VER EL CARRITO
# ===============================================
def ver_carrito_view(request):
    carrito = request.session.get('carrito', {})
    items = []
    total_pedido = 0

    for producto_id, item in carrito.items():
        subtotal = item['cantidad'] * item['precio']
        items.append({
            'producto_id': producto_id,
            'nombre': item['nombre'],
            'cantidad': item['cantidad'],
            'precio': item['precio'],
            'subtotal': subtotal
        })
        total_pedido += subtotal

    return render(request, 'carrito.html', {'items': items, 'total_pedido': total_pedido})

# ===============================================
# VISTA PARA CONFIRMAR EL PEDIDO (GUARDAR EN BD)
# ===============================================
@login_required(login_url='login') # Proteger esta vista
def confirmar_pedido_view(request):
    carrito = request.session.get('carrito', {})
    if not carrito:
        messages.error(request, 'Tu carrito está vacío.')
        return redirect('menu_page')

    try:
        # Asumimos que el Cliente está enlazado al User
        cliente_actual = request.user.cliente
    except Cliente.DoesNotExist:
        messages.error(request, 'Error: Tu usuario no está enlazado a un perfil de cliente.')
        return redirect('home')

    # 1. Crear el Pedido (la cabecera)
    nuevo_pedido = Pedido.objects.create(
        usuario=request.user,
        # 'mesa' se deja en null, asumiendo que es un pedido online o se asignará después
        estado_pedido='PENDIENTE' 
        # El total se calculará ahora
    )
    
    total_final = 0
    
    # 2. Crear los Detalles del Pedido
    for producto_id, item_data in carrito.items():
        producto = get_object_or_404(Producto, id=int(producto_id))
        cantidad = item_data['cantidad']
        precio_unitario = item_data['precio']
        subtotal = cantidad * precio_unitario
        
        DetallePedido.objects.create(
            pedido=nuevo_pedido,
            producto=producto,
            cantidad=cantidad,
            precio_unitario=precio_unitario,
            subtotal=subtotal # Asignamos el subtotal calculado
        )
        total_final += subtotal
    
    # 3. Actualizar el total del pedido
    nuevo_pedido.total = total_final
    nuevo_pedido.save()
    
    # 4. Limpiar el carrito de la sesión
    del request.session['carrito']
    
    # 5. Redirigir a página de éxito
    return redirect('pedido_exitoso')


def pedido_exitoso_view(request):
    return render(request, 'pedido_exitoso.html')