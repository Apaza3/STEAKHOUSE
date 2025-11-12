from django.shortcuts import render

from .models import Producto

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Producto

from .models import Producto, Pedido, DetallePedido

def menu_view(request):
    categorias = Producto.CATEGORIA_CHOICES
    
    # CAMBIO: Usamos .all() para traer TODO, sin importar si está disponible o no
    productos = Producto.objects.all() 
    
    context = {
        'categorias': categorias,
        'productos': productos,
    }
    return render(request, 'menu.html', context)

def agregar_al_carrito(request, producto_id):
    """Añade un producto a la sesión del usuario."""
    # 1. Obtener el carrito de la sesión (o crear uno vacío si no existe)
    carrito = request.session.get('carrito', {})
    
    # 2. Convertir el ID a string (las sesiones usan claves string)
    producto_id_str = str(producto_id)
    
    # 3. Si el producto ya está, aumentamos la cantidad. Si no, lo añadimos.
    if producto_id_str in carrito:
        carrito[producto_id_str] += 1
    else:
        carrito[producto_id_str] = 1
        
    # 4. Guardar el carrito actualizado en la sesión
    request.session['carrito'] = carrito
    
    messages.success(request, 'Producto añadido a tu pedido.')
    # Recargamos la misma página del menú
    return redirect('menu_page')

def ver_carrito(request):
    """Muestra el resumen del pedido actual."""
    carrito = request.session.get('carrito', {})
    items_carrito = []
    total_pedido = 0
    
    # Recuperamos los objetos Producto reales basados en los IDs de la sesión
    for producto_id, cantidad in carrito.items():
        producto = get_object_or_404(Producto, id=int(producto_id))
        subtotal = producto.precio * cantidad
        total_pedido += subtotal
        items_carrito.append({
            'producto': producto,
            'cantidad': cantidad,
            'subtotal': subtotal
        })
        
    context = {
        'items_carrito': items_carrito,
        'total_pedido': total_pedido
    }
    return render(request, 'carrito.html', context)


def confirmar_pedido(request):
    """Toma el carrito de la sesión y crea un Pedido en la BD."""
    carrito = request.session.get('carrito', {})
    
    if not carrito:
        messages.error(request, "Tu carrito está vacío.")
        return redirect('menu_page')

    try:
        # 1. Creamos la cabecera del Pedido
        # (Por ahora sin usuario ni mesa, lo mejoraremos luego)
        nuevo_pedido = Pedido.objects.create(
            estado_pedido='PENDIENTE',
            total=0 # Lo calcularemos ahora
        )

        total_pedido = 0
        
        # 2. Creamos los detalles (los ítems)
        for producto_id, cantidad in carrito.items():
            producto = Producto.objects.get(id=int(producto_id))
            subtotal = producto.precio * cantidad
            
            DetallePedido.objects.create(
                pedido=nuevo_pedido,
                producto=producto,
                cantidad=cantidad,
                precio_unitario=producto.precio, # Guardamos el precio actual
                subtotal=subtotal
            )
            total_pedido += subtotal

        # 3. Actualizamos el total del pedido
        nuevo_pedido.total = total_pedido
        nuevo_pedido.save()

        # 4. Vaciamos el carrito de la sesión
        del request.session['carrito']
        request.session.modified = True

        # 5. Redirigimos a la página de éxito
        return redirect('pedido_exitoso', pedido_id=nuevo_pedido.id)

    except Exception as e:
        print(f"Error al crear pedido: {e}")
        messages.error(request, "Hubo un error al procesar tu pedido.")
        return redirect('ver_carrito')

def pedido_exitoso(request, pedido_id):
    """Muestra la confirmación final."""
    pedido = get_object_or_404(Pedido, id=pedido_id)
    return render(request, 'pedido_exitoso.html', {'pedido': pedido})
