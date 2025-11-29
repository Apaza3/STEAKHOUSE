from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.models import User
from clientes.models import Cliente
from core.models import Mesa
from productos.models import Producto
from productos.forms import ProductoForm
from .forms import MesaForm, EmpleadoCreateForm
from pedidos.models import Pedido, DetallePedido
from reservas.models import Reserva
from django.db.models import Sum, Count, F
import json

# --- IMPORTACIONES PARA PDF ---
from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa
from django.utils import timezone

# ===============================================
# DECORADORES
# ===============================================

def staff_requerido(function):
    return user_passes_test(
        lambda u: u.is_authenticated and u.is_staff,
        login_url='login',
        redirect_field_name=None
    )(function)

def admin_requerido(function):
    return user_passes_test(
        lambda u: u.is_authenticated and u.is_superuser,
        login_url='dashboard_home',
        redirect_field_name=None
    )(function)

# ===============================================
# VISTA PRINCIPAL (LA QUE TE FALTABA)
# ===============================================

@staff_requerido
def dashboard_home(request):
    return redirect('dashboard_reservas')

# ===============================================
# VISTAS DE PRODUCTOS
# ===============================================
@admin_requerido
def producto_list(request):
    productos = Producto.objects.all().order_by('nombre_producto')
    return render(request, 'dashboard/producto_list.html', {'productos': productos})

@admin_requerido
def producto_create(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto creado exitosamente.')
            return redirect('dashboard_productos')
    else:
        form = ProductoForm()
    return render(request, 'dashboard/producto_form.html', {'form': form, 'titulo': 'Crear Nuevo Producto'})

@admin_requerido
def producto_update(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto actualizado exitosamente.')
            return redirect('dashboard_productos')
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'dashboard/producto_form.html', {'form': form, 'titulo': f'Editar {producto.nombre_producto}'})

@admin_requerido
def producto_delete(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        producto.delete()
        messages.success(request, 'Producto eliminado.')
        return redirect('dashboard_productos')
    return render(request, 'dashboard/producto_delete.html', {'producto': producto})

# ===============================================
# VISTAS DE MESAS
# ===============================================
@admin_requerido
def mesa_list(request):
    mesas = Mesa.objects.all().order_by('numero')
    return render(request, 'dashboard/mesa_list.html', {'mesas': mesas})

@admin_requerido
def mesa_create(request):
    if request.method == 'POST':
        form = MesaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Mesa creada exitosamente.')
            return redirect('dashboard_mesas')
    else:
        form = MesaForm()
    return render(request, 'dashboard/mesa_form.html', {'form': form, 'titulo': 'Crear Nueva Mesa'})

@admin_requerido
def mesa_update(request, pk):
    mesa = get_object_or_404(Mesa, pk=pk)
    if request.method == 'POST':
        form = MesaForm(request.POST, instance=mesa)
        if form.is_valid():
            form.save()
            messages.success(request, f'Mesa {mesa.numero} actualizada.')
            return redirect('dashboard_mesas')
    else:
        form = MesaForm(instance=mesa)
    return render(request, 'dashboard/mesa_form.html', {'form': form, 'titulo': f'Editar Mesa {mesa.numero}'})

@admin_requerido
def mesa_delete(request, pk):
    mesa = get_object_or_404(Mesa, pk=pk)
    if request.method == 'POST':
        mesa.delete()
        messages.success(request, f'Mesa {mesa.numero} eliminada.')
        return redirect('dashboard_mesas')
    return render(request, 'dashboard/mesa_delete.html', {'mesa': mesa})

# ===============================================
# VISTAS DE USUARIOS
# ===============================================
@admin_requerido
def empleado_list(request):
    usuarios = User.objects.filter(is_staff=True).order_by('username')
    return render(request, 'dashboard/user_list.html', { 'usuarios': usuarios })

@admin_requerido
def cliente_list(request):
    clientes = User.objects.filter(is_staff=False).order_by('username')
    return render(request, 'dashboard/client_list.html', { 'usuarios': clientes })

@admin_requerido
def user_toggle_staff(request, user_id):
    if request.user.id == user_id:
        messages.error(request, "No puedes cambiar tu propio estado.")
        return redirect('dashboard_empleados')
    user = get_object_or_404(User, id=user_id)
    user.is_staff = not user.is_staff
    user.save()
    estado = "Administrador" if user.is_staff else "Usuario normal"
    messages.success(request, f"'{user.username}' ahora es {estado}.")
    return redirect('dashboard_empleados')

@admin_requerido
def user_delete(request, user_id):
    if request.user.id == user_id:
        messages.error(request, "No puedes eliminarte a ti mismo.")
        return redirect('dashboard_empleados')
    user = get_object_or_404(User, id=user_id)
    user.delete() 
    messages.success(request, "Usuario eliminado permanentemente.")
    return redirect('dashboard_empleados')

@admin_requerido
def empleado_create_view(request):
    if request.method == 'POST':
        form = EmpleadoCreateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Nuevo empleado creado.')
            return redirect('dashboard_empleados')
        else:
            messages.error(request, 'Error al crear el empleado.')
    else:
        form = EmpleadoCreateForm()
    return render(request, 'dashboard/empleado_form.html', {'form': form, 'titulo': 'Crear Nuevo Empleado'})

# ===============================================
# VISTAS DE PEDIDOS
# ===============================================
@staff_requerido
def pedido_list(request):
    pedidos = Pedido.objects.all().order_by('-fecha_pedido')
    return render(request, 'dashboard/pedido_list.html', {'pedidos': pedidos})

@staff_requerido
def pedido_detail(request, pk):
    pedido = get_object_or_404(Pedido, pk=pk)
    if request.method == 'POST':
        nuevo_estado = request.POST.get('estado_pedido')
        redirect_to = request.POST.get('redirect_to', 'detail') 
        if nuevo_estado in [choice[0] for choice in Pedido.ESTADO_PEDIDO_CHOICES]:
            pedido.estado_pedido = nuevo_estado
            pedido.save()
            messages.success(request, f'Estado actualizado a {pedido.get_estado_pedido_display()}.')
            if redirect_to == 'list':
                return redirect('dashboard_pedidos')
            else:
                return redirect('pedido_detail', pk=pedido.pk)
    return render(request, 'dashboard/pedido_detail.html', {'pedido': pedido})

# ===============================================
# VISTAS DE RESERVAS
# ===============================================
@staff_requerido
def reserva_list(request):
    reservas = Reserva.objects.all().order_by('-fecha_reserva', '-hora_reserva')
    return render(request, 'dashboard/reserva_list.html', {'reservas': reservas})

# ===============================================
# VISTA DE REPORTES
# ===============================================
@admin_requerido
def reportes_view(request):
    
    # 1. Usamos las opciones DIRECTO del modelo
    lista_categorias = Producto.CATEGORIA_CHOICES
    
    categoria_key = request.GET.get('categoria')

    # Query Base
    ventas = Pedido.objects.filter(estado_pedido='ENTREGADO').order_by('-fecha_pedido')

    # --- LÓGICA DEL FILTRO ---
    if categoria_key:
        # ¡CORRECCIÓN AQUÍ! Usamos 'detalles' en lugar de 'detallepedido'
        ventas = ventas.filter(detalles__producto__categoria=categoria_key).distinct()

    # 2. KPIS GENERALES
    ventas_totales_query = Pedido.objects.filter(estado_pedido='ENTREGADO')
    total_ventas = ventas_totales_query.aggregate(Sum('total'))['total__sum'] or 0.00
    num_ventas = ventas_totales_query.count()
    
    reservas_pagadas = Reserva.objects.filter(estado__in=['CONFIRMADA', 'COMPLETADA'])
    total_reservas = reservas_pagadas.aggregate(Sum('monto_pagado'))['monto_pagado__sum'] or 0.00
    num_reservas = reservas_pagadas.count()

    # 3. DATOS GRÁFICOS (También corregimos aquí si usabas detallepedido, aunque parece que usas el modelo directo)
    # Nota: Aquí usas DetallePedido.objects... eso está bien si importaste el modelo.
    platos_vendidos = DetallePedido.objects.filter(pedido__estado_pedido='ENTREGADO') \
        .values('producto__nombre_producto') \
        .annotate(total_vendido=Sum('cantidad')) \
        .order_by('-total_vendido')[:5]
    platos_labels = [item['producto__nombre_producto'] for item in platos_vendidos]
    platos_data = [item['total_vendido'] for item in platos_vendidos]

    tipos_mesa_pop = Reserva.objects \
        .filter(estado__in=['CONFIRMADA', 'COMPLETADA'], mesa__isnull=False) \
        .values('mesa__tipo') \
        .annotate(conteo=Count('id')) \
        .order_by('mesa__tipo')
    tipos_labels = [item['mesa__tipo'].capitalize() for item in tipos_mesa_pop]
    tipos_data = [item['conteo'] for item in tipos_mesa_pop]

    tamanos_grupo = Reserva.objects \
        .filter(estado__in=['CONFIRMADA', 'COMPLETADA']) \
        .values('numero_personas') \
        .annotate(conteo=Count('id')) \
        .order_by('numero_personas')
    tamanos_labels = [f"{item['numero_personas']} personas" for item in tamanos_grupo]
    tamanos_data = [item['conteo'] for item in tamanos_grupo]

    # 4. CONTEXTO
    context = {
        'lista_categorias': lista_categorias, 
        'categoria_seleccionada': categoria_key, 
        'ventas': ventas, 
        'total_ventas': total_ventas,
        'num_ventas': num_ventas,
        'total_reservas': total_reservas,
        'num_reservas': num_reservas,
        'reservas': reservas_pagadas.order_by('-fecha_reserva')[:20],
        'platos_labels': json.dumps(platos_labels),
        'platos_data': json.dumps(platos_data),
        'tipos_labels': json.dumps(tipos_labels),
        'tipos_data': json.dumps(tipos_data),
        'tamanos_labels': json.dumps(tamanos_labels),
        'tamanos_data': json.dumps(tamanos_data),
    }
    return render(request, 'dashboard/reportes_view.html', context)


# ===============================================
# VISTA PDF (CORREGIDA: 'detalles' en vez de 'detallepedido')
# ===============================================
@admin_requerido
def generar_pdf_view(request):
    categoria_key = request.GET.get('categoria')
    
    ventas = Pedido.objects.filter(estado_pedido='ENTREGADO').order_by('-fecha_pedido')
    titulo_reporte = "Reporte General de Ventas"
    
    if categoria_key:
        # ¡CORRECCIÓN AQUÍ TAMBIÉN!
        ventas = ventas.filter(detalles__producto__categoria=categoria_key).distinct()
        
        nombre_categoria = dict(Producto.CATEGORIA_CHOICES).get(categoria_key, categoria_key)
        titulo_reporte = f"Reporte de Ventas: {nombre_categoria}"

    total_dinero = ventas.aggregate(Sum('total'))['total__sum'] or 0.00

    context = {
        'ventas': ventas,
        'titulo_reporte': titulo_reporte,
        'total_dinero': total_dinero,
        'fecha_emision': timezone.now(),
        'usuario': request.user
    }

    template_path = 'dashboard/pdf_template.html'
    template = get_template(template_path)
    html = template.render(context)

    response = HttpResponse(content_type='application/pdf')
    filename = f"reporte_{timezone.now().strftime('%Y%m%d')}.pdf"
    response['Content-Disposition'] = f'inline; filename="{filename}"'

    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('Error al generar PDF')
    return response