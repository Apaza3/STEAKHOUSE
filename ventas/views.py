# ventas/views.py

from django.shortcuts import render
# Importaciones para ambas vistas
from .models import CategoriaProducto, Producto, Pedido, DetallePedido
from types import SimpleNamespace 
from django.db.models import Sum, Count
from datetime import date

# ----------------------------------------
# VISTA PARA MOSTRAR EL MENÚ
# ----------------------------------------
def mostrar_menu(request):
    """
    Muestra el menú de productos, agrupados por categoría.
    Incluye datos falsos si la base de datos está vacía.
    """
    
    # 1. Intentamos obtener las categorías REALES de la base de datos
    categorias = CategoriaProducto.objects.prefetch_related('productos')

    # 2. Revisamos si la consulta de la base de datos vino vacía
    if not categorias.exists():
        
        # --- Si está vacía, creamos datos FALSOS ---
        
        # Creamos 3 productos falsos (con imágenes y precio en Bs)
        p1 = SimpleNamespace(
            nombre='Corte Falso (Prueba)', 
            precio='120.50', 
            descripcion='Una deliciosa descripción de prueba para ver el layout.', 
            disponible=True,
            imagen='https://picsum.photos/400/300?image=1070' 
        )
        p2 = SimpleNamespace(
            nombre='Hamburguesa de Prueba', 
            precio='75.00', 
            descripcion='Hamburguesa de la casa para probar el diseño de la tarjeta.', 
            disponible=True,
            imagen='https://picsum.photos/400/300?image=1080'
        )
        p3 = SimpleNamespace(
            nombre='Otro Plato Falso', 
            precio='88.00', 
            descripcion='Descripción para la tercera tarjeta de producto.', 
            disponible=True,
            imagen='https://picsum.photos/400/300?image=835'
        )

        # Creamos una categoría falsa que contiene esos productos
        cat1 = SimpleNamespace(
            nombre='Categoría de Prueba (Layout)', 
            productos=SimpleNamespace(all=[p1, p2, p3])
        )
        
        # Reemplazamos la variable 'categorias' (que estaba vacía)
        # con nuestra lista de datos falsos.
        categorias = [cat1]
        # --- Fin de los datos falsos ---


    # 3. Preparamos los datos para enviar al HTML
    contexto = {
        'categorias': categorias
    }
    
    # 4. Renderizamos el archivo HTML
    return render(request, 'menu.html', contexto)


# ----------------------------------------
# VISTA PARA EL REPORTE DE VENTAS
# ----------------------------------------
def ver_reporte_ventas(request):
    """
    Esta vista maneja la lógica del reporte de ventas.
    """
    
    # 1. Obtener la fecha de la URL (si existe)
    fecha_filtro = request.GET.get('fecha', None)
    
    # 2. Empezar con los pedidos pagados
    # (Generalmente solo reportas sobre ventas completadas)
    pedidos_query = Pedido.objects.filter(estado='pagado')

    # 3. Filtrar por fecha si se proporcionó una
    if fecha_filtro:
        try:
            # Convertir el texto de la URL a un objeto fecha
            fecha = date.fromisoformat(fecha_filtro)
            # Filtrar el queryset por esa fecha exacta
            pedidos_query = pedidos_query.filter(creado_en__date=fecha)
        except ValueError:
            # Si la fecha es inválida, simplemente ignora el filtro
            pass 

    # 4. Calcular el resumen (Totales)
    resumen = pedidos_query.aggregate(
        total_ventas=Sum('total'),    # Suma de la columna 'total'
        total_pedidos=Count('id')   # Conteo de N° de pedidos
    )

    # 5. Preparar el contexto para el HTML
    contexto = {
        'pedidos': pedidos_query.order_by('-creado_en'), # Mostrar los más nuevos primero
        'resumen': resumen,
        'fecha_filtro': fecha_filtro # Para rellenar el campo de fecha
    }

    # 5. Renderizar la nueva plantilla HTML (reporte_ventas.html)
    return render(request, 'reporte_ventas.html', contexto)