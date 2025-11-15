from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Pedido, DetallePedido
from clientes.models import Cliente
from productos.models import Producto
from collections import defaultdict

# --- ¡CAMBIO! ESTA ES LA ÚNICA IMPORTACIÓN DE EMAIL QUE NECESITAS ---
from core.utils import enviar_email_automatico 
# from django.core.mail import send_mail # <-- YA NO SE USA AQUÍ
from django.template.loader import render_to_string # <-- No se usa aquí, pero está bien
from django.conf import settings
# ------------------------------------

# ===============================================
# VISTA DEL MENÚ (Sin cambios)
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
# VISTA PARA AÑADIR AL CARRITO (Sin cambios)
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
# VISTA PARA VER EL CARRITO (Sin cambios)
# ===============================================
@login_required(login_url='login')
def ver_carrito_view(request):
    return redirect('menu_page')

# ===============================================
# VISTA PARA CONFIRMAR EL PEDIDO (¡SECCIÓN DE EMAIL CORREGIDA!)
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
        estado_pedido='PENDIENTE', # ¡CAMBIO IMPORTANTE! Guardar primero y LUEGO enviar email
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
    
    # 3. Actualizar el total y estado final
    nuevo_pedido.total = total_final
    nuevo_pedido.estado_pedido = 'COMPLETADO' # O 'CONFIRMADO'
    nuevo_pedido.save()
    
    # --- 4. ENVIAR FACTURA POR EMAIL (¡CORREGIDO!) ---
    
    # Preparamos los datos
    asunto = f"Confirmación de tu Pedido #{nuevo_pedido.id} en The Steakhouse"
    contexto_email = {
        'pedido': nuevo_pedido,
        'detalles': detalles_para_email,
        'cliente': cliente_actual,
        'usuario': request.user,
    }
    template_path = 'emails/factura_pedido.html'
    email_destino = request.user.email

    # ¡ESTE ES EL CAMBIO!
    # Llamamos a la función asíncrona de utils.py
    # Esto se ejecuta en 1 milisegundo y no bloquea el servidor.
    enviar_email_automatico(
        template_path=template_path,
        context_datos=contexto_email,
        asunto=asunto,
        email_destino=email_destino
    )

    # --- (INICIO DE CÓDIGO ANTIGUO ELIMINADO) ---
    # try:
    #     html_message = render_to_string('emails/factura_pedido.html', contexto_email)
    #     send_mail( ... ) # <-- ESTO ES LO QUE CAUSABA EL TIMEOUT DE 30 SEGUNDOS
    # except Exception as e:
    #     print(f"ERROR AL ENVIAR EMAIL de pedido: {e}") 
    #     messages.warning(request, 'Pedido confirmado, pero hubo un error al enviar tu factura por email.')
    # --- (FIN DE CÓDIGO ANTIGUO ELIMINADO) ---

    # 5. Limpiar el carrito
    del request.session['carrito']
    
    messages.success(request, '¡Pedido confirmado! Hemos recibido tu orden.')
    
    return redirect('pedido_exitoso')

# ===============================================
# VISTA DE ÉXITO (Sin cambios)
# ===============================================
@login_required(login_url='login')
def pedido_exitoso_view(request):
    return render(request, 'pedidos/pedido_exitoso.html')

# ===============================================
# VISTA "MIS PEDIDOS" (Sin cambios)
# ===============================================
@login_required(login_url='login')
def mis_pedidos_view(request):
    pedidos = Pedido.objects.filter(usuario=request.user).order_by('-fecha_pedido')
    
    context = {
        'pedidos': pedidos
    }
    return render(request, 'pedidos/mis_pedidos.html', context)