from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.models import User
from clientes.models import Cliente
from productos.models import Producto
from productos.forms import ProductoForm
from pedidos.models import Pedido, DetallePedido

# ===============================================
# DECORADOR PARA PROTEGER VISTAS DE ADMIN
# ===============================================
def admin_requerido(function):
    return user_passes_test(
        lambda u: u.is_authenticated and u.is_staff,
        login_url='login',
        redirect_field_name=None
    )(function)

# ===============================================
# VISTA PRINCIPAL DEL PANEL
# ===============================================
@admin_requerido
def dashboard_home(request):
    return redirect('dashboard_pedidos')

# ===============================================
# VISTAS DEL PANEL DE PRODUCTOS (CRUD)
# ===============================================
@admin_requerido
def producto_list(request):
    productos = Producto.objects.all().order_by('nombre_producto')
    context = {'productos': productos}
    return render(request, 'dashboard/producto_list.html', context)

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
    context = {'form': form}
    return render(request, 'dashboard/producto_form.html', context)

# --- ¡AQUÍ ESTÁ LA CORRECCIÓN DEL TYPO! ---
@admin_requerido 
# (Antes decía @admin_bupper)
# --- FIN DE LA CORRECCIÓN ---
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
    context = {'form': form, 'producto': producto}
    return render(request, 'dashboard/producto_form.html', context)

@admin_requerido
def producto_delete(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        producto.delete()
        messages.success(request, 'Producto eliminado.')
        return redirect('dashboard_productos')
    context = {'producto': producto}
    return render(request, 'dashboard/producto_delete.html', context)

# ===============================================
# VISTAS DE GESTIÓN DE USUARIOS
# ===============================================
@admin_requerido
def user_list(request):
    usuarios = User.objects.all().order_by('username')
    context = { 'usuarios': usuarios }
    return render(request, 'dashboard/user_list.html', context)

@admin_requerido
def user_toggle_staff(request, user_id):
    if request.user.id == user_id:
        messages.error(request, "No puedes cambiar tu propio estado de administrador.")
        return redirect('dashboard_usuarios')
    user = get_object_or_404(User, id=user_id)
    user.is_staff = not user.is_staff
    user.save()
    if user.is_staff:
        messages.success(request, f"'{user.username}' ha sido promovido a Administrador.")
    else:
        messages.success(request, f"'{user.username}' ha sido degradado a Usuario normal.")
    return redirect('dashboard_usuarios')

@admin_requerido
def user_delete(request, user_id):
    if request.user.id == user_id:
        messages.error(request, "No puedes eliminarte a ti mismo.")
        return redirect('dashboard_usuarios')
    user = get_object_or_404(User, id=user_id)
    username = user.username
    user.delete() 
    messages.success(request, f"El usuario '{username}' ha sido eliminado permanentemente.")
    return redirect('dashboard_usuarios')

# ===============================================
# VISTA DE REPORTES DE VENTAS
# ===============================================
@admin_requerido
def reportes_ventas_view(request):
    context = {}
    return render(request, 'dashboard/reportes_ventas.html', context)


# ===============================================
# VISTAS DE GESTIÓN DE PEDIDOS
# ===============================================

@admin_requerido
def pedido_list(request):
    pedidos = Pedido.objects.all().order_by('-fecha_pedido')
    context = {
        'pedidos': pedidos
    }
    return render(request, 'dashboard/pedido_list.html', context)

@admin_requerido
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