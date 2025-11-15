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

# ===============================================
# ¡CAMBIO! DECORADORES DE SEGURIDAD
# ===============================================

def staff_requerido(function):
    """
    Decorador que verifica que el usuario sea un empleado (is_staff).
    Usado para vistas generales del panel (ej. ver reservas, ver pedidos).
    """
    return user_passes_test(
        lambda u: u.is_authenticated and u.is_staff,
        login_url='login',
        redirect_field_name=None
    )(function)

def admin_requerido(function):
    """
    Decorador que verifica que el usuario sea un SUPERUSUARIO (is_superuser).
    Usado para vistas sensibles (ej. crear empleados, productos, mesas, ver reportes).
    """
    return user_passes_test(
        lambda u: u.is_authenticated and u.is_superuser,
        login_url='dashboard_home', # Si no es admin, lo manda al inicio del panel
        redirect_field_name=None
    )(function)

# ===============================================

@staff_requerido # <-- CAMBIO
def dashboard_home(request):
    return redirect('dashboard_reservas')

# ===============================================
# VISTAS DEL PANEL DE PRODUCTOS (CRUD)
# ===============================================
@admin_requerido # <-- CAMBIO
def producto_list(request):
    productos = Producto.objects.all().order_by('nombre_producto')
    context = {'productos': productos}
    return render(request, 'dashboard/producto_list.html', context)

@admin_requerido # <-- CAMBIO
def producto_create(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto creado exitosamente.')
            return redirect('dashboard_productos')
    else:
        form = ProductoForm()
    context = {'form': form, 'titulo': 'Crear Nuevo Producto'}
    return render(request, 'dashboard/producto_form.html', context)

@admin_requerido # <-- CAMBIO
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
    context = {'form': form, 'titulo': f'Editar {producto.nombre_producto}'}
    return render(request, 'dashboard/producto_form.html', context)

@admin_requerido # <-- CAMBIO
def producto_delete(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        producto.delete()
        messages.success(request, 'Producto eliminado.')
        return redirect('dashboard_productos')
    context = {'producto': producto}
    return render(request, 'dashboard/producto_delete.html', context)

# ===============================================
# VISTAS DE GESTIÓN DE MESAS (CRUD)
# ===============================================
@admin_requerido # <-- CAMBIO
def mesa_list(request):
    mesas = Mesa.objects.all().order_by('numero')
    context = {'mesas': mesas}
    return render(request, 'dashboard/mesa_list.html', context)

@admin_requerido # <-- CAMBIO
def mesa_create(request):
    if request.method == 'POST':
        form = MesaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Mesa creada exitosamente.')
            return redirect('dashboard_mesas')
    else:
        form = MesaForm()
    context = {'form': form, 'titulo': 'Crear Nueva Mesa'}
    return render(request, 'dashboard/mesa_form.html', context)

@admin_requerido # <-- CAMBIO
def mesa_update(request, pk):
    mesa = get_object_or_404(Mesa, pk=pk)
    if request.method == 'POST':
        form = MesaForm(request.POST, instance=mesa)
        if form.is_valid():
            form.save()
            messages.success(request, f'Mesa {mesa.numero} actualizada exitosamente.')
            return redirect('dashboard_mesas')
    else:
        form = MesaForm(instance=mesa)
    context = {'form': form, 'titulo': f'Editar Mesa {mesa.numero}'}
    return render(request, 'dashboard/mesa_form.html', context)

@admin_requerido # <-- CAMBIO
def mesa_delete(request, pk):
    mesa = get_object_or_404(Mesa, pk=pk)
    if request.method == 'POST':
        mesa.delete()
        messages.success(request, f'Mesa {mesa.numero} eliminada.')
        return redirect('dashboard_mesas')
    context = {'mesa': mesa}
    return render(request, 'dashboard/mesa_delete.html', context)

# ===============================================
# VISTAS DE GESTIÓN DE USUARIOS
# ===============================================
@admin_requerido # <-- CAMBIO
def empleado_list(request):
    usuarios = User.objects.filter(is_staff=True).order_by('username')
    context = { 'usuarios': usuarios }
    return render(request, 'dashboard/user_list.html', context)

@admin_requerido # <-- CAMBIO
def cliente_list(request):
    clientes = User.objects.filter(is_staff=False).order_by('username')
    context = { 'usuarios': clientes }
    return render(request, 'dashboard/client_list.html', context)

@admin_requerido # <-- CAMBIO
def user_toggle_staff(request, user_id):
    if request.user.id == user_id:
        messages.error(request, "No puedes cambiar tu propio estado de administrador.")
        return redirect('dashboard_empleados')
    user = get_object_or_404(User, id=user_id)
    user.is_staff = not user.is_staff
    user.save()
    if user.is_staff:
        messages.success(request, f"'{user.username}' ha sido promovido a Administrador.")
    else:
        messages.success(request, f"'{user.username}' ha sido degradado a Usuario normal.")
    return redirect('dashboard_empleados')

@admin_requerido # <-- CAMBIO
def user_delete(request, user_id):
    if request.user.id == user_id:
        messages.error(request, "No puedes eliminarte a ti mismo.")
        return redirect('dashboard_empleados')
    user = get_object_or_404(User, id=user_id)
    username = user.username
    user.delete() 
    messages.success(request, f"El usuario '{username}' ha sido eliminado permanentemente.")
    return redirect('dashboard_empleados')

# ===================================================
# VISTA PARA CREAR EMPLEADOS
# ===================================================
@admin_requerido # <-- CAMBIO
def empleado_create_view(request):
    if request.method == 'POST':
        form = EmpleadoCreateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Nuevo empleado creado exitosamente.')
            return redirect('dashboard_empleados')
        else:
            messages.error(request, 'Error al crear el empleado. Revisa los campos.')
    else:
        form = EmpleadoCreateForm()
    
    context = {
        'form': form,
        'titulo': 'Crear Nuevo Empleado'
    }
    return render(request, 'dashboard/empleado_form.html', context)

# ===============================================
# VISTAS DE GESTIÓN DE PEDIDOS
# ===============================================
@staff_requerido # <-- CAMBIO
def pedido_list(request):
    pedidos = Pedido.objects.all().order_by('-fecha_pedido')
    context = {
        'pedidos': pedidos
    }
    return render(request, 'dashboard/pedido_list.html', context)

@staff_requerido # <-- CAMBIO
def pedido_detail(request, pk):
    pedido = get_object_or_404(Pedido, pk=pk)
    
    if request.method == 'POST':
        nuevo_estado = request.POST.get('estado_pedido')
        if nuevo_estado in [choice[0] for choice in Pedido.ESTADO_PEDIDO_CHOICES]:
            pedido.estado_pedido = nuevo_estado
            pedido.save()
            messages.success(request, f'Estado del Pedido #{pedido.id} actualizado a {pedido.get_estado_pedido_display()}.')
            return redirect('pedido_detail', pk=pedido.pk)
            
    context = {
        'pedido': pedido
    }
    return render(request, 'dashboard/pedido_detail.html', context)

# ===============================================
# VISTAS DE GESTIÓN DE RESERVAS
# ===============================================
@staff_requerido # <-- CAMBIO
def reserva_list(request):
    reservas = Reserva.objects.all().order_by('-fecha_reserva', '-hora_reserva')
    context = {
        'reservas': reservas
    }
    return render(request, 'dashboard/reserva_list.html', context)
    
# ===============================================
# VISTA DE REPORTES
# ===============================================
@admin_requerido # <-- CAMBIO
def reportes_view(request):
    
    # --- 1. DATOS PARA KPIs (Como antes) ---
    ventas = Pedido.objects.filter(estado_pedido='ENTREGADO')
    total_ventas = ventas.aggregate(Sum('total'))['total__sum'] or 0.00
    num_ventas = ventas.count()
    
    reservas_pagadas = Reserva.objects.filter(estado__in=['CONFIRMADA', 'COMPLETADA'])
    total_reservas = reservas_pagadas.aggregate(Sum('monto_pagado'))['monto_pagado__sum'] or 0.00
    num_reservas = reservas_pagadas.count()

    # --- 2. DATOS PARA GRÁFICOS (¡NUEVO!) ---
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

    # --- 3. CONTEXTO ---
    context = {
        'total_ventas': total_ventas,
        'num_ventas': num_ventas,
        'total_reservas': total_reservas,
        'num_reservas': num_reservas,
        'ventas': ventas.order_by('-fecha_pedido')[:20],
        'reservas': reservas_pagadas.order_by('-fecha_reserva')[:20],
        'platos_labels': json.dumps(platos_labels),
        'platos_data': json.dumps(platos_data),
        'tipos_labels': json.dumps(tipos_labels),
        'tipos_data': json.dumps(tipos_data),
        'tamanos_labels': json.dumps(tamanos_labels),
        'tamanos_data': json.dumps(tamanos_data),
    }
    return render(request, 'dashboard/reportes_view.html', context)