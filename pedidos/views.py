from django.shortcuts import render
from .models import Producto

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Producto

def menu_view(request):
    # Obtenemos todas las categorías para filtrar en el futuro
    categorias = Producto.CATEGORIA_CHOICES
    
    # Obtenemos los productos reales de la BD (aunque ahora esté vacía)
    productos = Producto.objects.filter(disponible=True)
    
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