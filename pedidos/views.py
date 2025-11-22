from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse 
from .models import Pedido, DetallePedido
from clientes.models import Cliente
from productos.models import Producto
from collections import defaultdict
from core.utils import enviar_email_automatico
from django.template.loader import render_to_string
from django.conf import settings

# --- FUNCIÓN AUXILIAR PARA HTML DEL CARRITO ---
def render_cart_html(request, carrito):
    """Genera el HTML de la tabla del carrito para actualizar el modal vía AJAX"""
    items = []
    total = 0
    cantidad_total = 0
    
    for pid, item in carrito.items():
        sub = float(item['precio']) * item['cantidad']
        total += sub
        cantidad_total += item['cantidad']
        items.append({
            'producto_id': pid,
            'nombre': item['nombre'],
            'cantidad': item['cantidad'],
            'precio': item['precio'],
            'subtotal': sub
        })
    
    # Renderizamos solo el cuerpo del carrito
    context = {'items_del_carrito': items, 'total_del_carrito': total}
    html = render_to_string('pedidos/includes/cart_body.html', context)
    return html, cantidad_total, total

# ===============================================
# VISTA DEL MENÚ (DISEÑO POR SECCIONES)
# ===============================================
# En pedidos/views.py

@login_required(login_url='login')
def menu_view(request):
    # 1. Obtener productos disponibles
    productos = Producto.objects.filter(disponible=True)
    
    # 2. Agrupar productos por categoría (Diccionario)
    # Esto crea algo como: {'HAMBURGUESA': [prod1, prod2], 'BEBIDA': [prod3]}
    agrupados = defaultdict(list)
    for p in productos:
        agrupados[p.categoria].append(p)
    
    # 3. Convertir las opciones del modelo a un diccionario para las pestañas
    # Esto permite que el HTML diga "Hamburguesas" en vez de "HAMBURGUESA"
    categorias_dict = dict(Producto.CATEGORIA_CHOICES)

    # 4. Datos del carrito (Mantenemos tu lógica que ya funcionaba)
    carrito = request.session.get('carrito', {})
    
    # Reconstruimos la lista para la vista inicial del modal
    items_lista = []
    total_calculado = 0
    cantidad_calculada = 0
    
    for pid, item in carrito.items():
        sub = float(item['precio']) * item['cantidad']
        total_calculado += sub
        cantidad_calculada += item['cantidad']
        items_lista.append({
            'producto_id': pid,
            'nombre': item['nombre'],
            'cantidad': item['cantidad'],
            'precio': item['precio'],
            'subtotal': sub
        })
    
    context = {
        # Estas son las variables EXACTAS que tu HTML nuevo pide:
        'categorias_choices': categorias_dict, 
        'productos_agrupados': dict(agrupados),
        
        # Variables del carrito
        'cantidad_total': cantidad_calculada,
        'total_del_carrito': total_calculado,
        'items_del_carrito': items_lista 
    }
    return render(request, 'menu.html', context)

# ===============================================
# AÑADIR AL CARRITO (AJAX + HTML)
# ===============================================
@login_required(login_url='login')
def agregar_al_carrito_view(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    carrito = request.session.get('carrito', {})
    pid = str(producto.id)
    
    if pid in carrito:
        carrito[pid]['cantidad'] += 1
    else:
        carrito[pid] = {
            'cantidad': 1, 
            'precio': str(producto.precio), 
            'nombre': producto.nombre_producto
        }
    
    request.session['carrito'] = carrito
    
    # Generamos el HTML actualizado del carrito
    html_carrito, cantidad, total = render_cart_html(request, carrito)
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'ok', 
            'cart_count': cantidad,
            'cart_html': html_carrito 
        })

    return redirect('menu_page')

# ===============================================
# ELIMINAR DEL CARRITO (AJAX + HTML)
# ===============================================
@login_required(login_url='login')
def eliminar_del_carrito_view(request, producto_id):
    carrito = request.session.get('carrito', {})
    pid = str(producto_id)

    if pid in carrito:
        del carrito[pid]
        request.session['carrito'] = carrito
    
    html_carrito, cantidad, total = render_cart_html(request, carrito)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'ok',
            'cart_count': cantidad,
            'cart_html': html_carrito
        })
    
    return redirect('menu_page')

# ===============================================
# VISTAS DE CONFIRMACIÓN (Sin cambios mayores)
# ===============================================
@login_required(login_url='login') 
def confirmar_pedido_view(request):
    carrito = request.session.get('carrito', {})
    if not carrito:
        messages.error(request, 'Tu carrito está vacío.')
        return redirect('menu_page')

    try:
        cliente = request.user.cliente 
    except Cliente.DoesNotExist:
        cliente = None 

    pedido = Pedido.objects.create(
        usuario=request.user,
        cliente=cliente,
        estado_pedido='PENDIENTE',
        total=0
    )
    
    total = 0
    detalles = []
    
    for pid, item in carrito.items():
        try:
            prod = Producto.objects.get(id=int(pid))
            detalle = DetallePedido.objects.create(
                pedido=pedido, producto=prod, cantidad=item['cantidad']
            )
            total += detalle.subtotal
            detalles.append(detalle)
        except Producto.DoesNotExist:
            continue
    
    pedido.total = total
    pedido.save()
    
    # Email (Asíncrono)
    try:
        enviar_email_automatico(
            template_path='emails/factura_pedido.html',
            context_datos={'pedido': pedido, 'detalles': detalles, 'cliente': cliente, 'usuario': request.user},
            asunto=f"Pedido #{pedido.id} Confirmado",
            email_destino=request.user.email
        )
    except:
        pass

    del request.session['carrito']
    messages.success(request, '¡Pedido confirmado!')
    return redirect('pedido_exitoso')

@login_required(login_url='login')
def pedido_exitoso_view(request):
    return render(request, 'pedido_exitoso.html')

@login_required(login_url='login')
def mis_pedidos_view(request):
    pedidos = Pedido.objects.filter(usuario=request.user).order_by('-fecha_pedido')
    return render(request, 'mis_pedidos.html', {'pedidos': pedidos})

@login_required(login_url='login')
def ver_carrito_view(request):
    return redirect('menu_page')