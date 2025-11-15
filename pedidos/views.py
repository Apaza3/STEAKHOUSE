from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Pedido, DetallePedido
from clientes.models import Cliente
from productos.models import Producto
from collections import defaultdict

# --- ¡NUEVAS IMPORTACIONES PARA EMAIL! ---
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
# ------------------------------------

# ===============================================
# VISTA DEL MENÚ (Actualizada para agrupar)
# ===============================================
@login_required(login_url='login')
def menu_view(request):
    
    # Obtenemos todos los productos y los preparamos para agrupar
    productos = Producto.objects.filter(disponible=True).order_by('categoria')
    
    # ¡CAMBIO! Agrupamos los productos por su VALOR de categoría (ej. 'CARNE')
    # Esto es para que los enlaces del header (#CARNE, #BEBIDA) funcionen
    productos_agrupados = defaultdict(list)
    for producto in productos:
        productos_agrupados[producto.categoria].append(producto)
    
    # Convertimos el defaultdict a un dict normal para el template
    productos_agrupados = dict(productos_agrupados)
    
    # Lógica del carrito (para el modal)
    carrito_session = request.session.get('carrito', {})
    items_del_carrito = []
    total_del_carrito = 0

    for producto_id, item in carrito_session.items():
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
        'productos_agrupados': productos_agrupados,
        # ¡NUEVO! Enviamos los nombres de las categorías para los títulos
        'categorias_choices': dict(Producto.CATEGORIA_CHOICES),
        'items_del_carrito': items_del_carrito,
        'total_del_carrito': total_del_carrito
    }
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
        carrito[producto_id_str] = {'cantidad': 1, 'precio': str(producto.precio), 'nombre': producto.nombre_producto}
    
    request.session['carrito'] = carrito
    messages.success(request, f"'{producto.nombre_producto}' añadido al carrito.")
    
    return redirect('menu_page')

# ===============================================
# VISTA PARA VER EL CARRITO (Simplificada)
# ===============================================
@login_required(login_url='login')
def ver_carrito_view(request):
    return redirect('menu_page')

# ===============================================
# VISTA PARA CONFIRMAR EL PEDIDO (¡CON ENVÍO DE EMAIL!)
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
        cliente_actual = None 
        messages.warning(request, 'Tu cuenta de admin no está enlazada a un perfil de cliente, el pedido se creará sin él.')

    # 1. Crear el Pedido
    nuevo_pedido = Pedido.objects.create(
        usuario=request.user,
        cliente=cliente_actual,
        estado_pedido='PENDIENTE',
        total = 0
    )
    
    total_final = 0
    detalles_para_email = []
    
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
        detalles_para_email.append(detalle)
    
    # 3. Actualizar el total
    nuevo_pedido.total = total_final
    nuevo_pedido.save()
    
    # --- 4. ENVIAR FACTURA POR EMAIL ---
    try:
        asunto = f"Confirmación de tu Pedido #{nuevo_pedido.id} en The Steakhouse"
        contexto_email = {
            'pedido': nuevo_pedido,
            'detalles': detalles_para_email,
            'cliente': cliente_actual,
            'usuario': request.user,
        }
        
        # ¡CAMBIO! Ruta corregida para que coincida con la de reservas
        html_message = render_to_string('emails/factura_pedido.html', contexto_email)
        
        send_mail(
            asunto,
            f"Hola {request.user.username}, tu pedido #{nuevo_pedido.id} ha sido confirmado. Total: {total_final} Bs.",
            settings.DEFAULT_FROM_EMAIL,
            [request.user.email],
            html_message=html_message,
            # ¡CAMBIO! Forzamos a que falle para que el 'except' atrape el error 535
            fail_silently=False 
        )
    except Exception as e:
        # Si el email falla, no crasheamos la app.
        print(f"ERROR AL ENVIAR EMAIL de pedido: {e}") # <-- Imprimirá el error 535
        messages.warning(request, 'Pedido confirmado, pero hubo un error al enviar tu factura por email.')
    # --- FIN DE SECCIÓN DE EMAIL ---

    # 5. Limpiar el carrito
    del request.session['carrito']
    
    messages.success(request, '¡Pedido confirmado! Hemos recibido tu orden.')
    
    return redirect('pedido_exitoso')

# ===============================================
# VISTA DE ÉXITO (Corregida)
# ===============================================
@login_required(login_url='login')
def pedido_exitoso_view(request):
    return render(request, 'pedidos/pedido_exitoso.html')

# ===============================================
# ¡NUEVA! VISTA "MIS PEDIDOS"
# ===============================================
@login_required(login_url='login')
def mis_pedidos_view(request):
    pedidos = Pedido.objects.filter(usuario=request.user).order_by('-fecha_pedido')
    
    context = {
        'pedidos': pedidos
    }
    return render(request, 'pedidos/mis_pedidos.html', context)