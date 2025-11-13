from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.models import User
from clientes.models import Cliente
from productos.models import Producto
from productos.forms import ProductoForm

# ===============================================
# DECORADOR PARA PROTEGER VISTAS DE ADMIN
# ===============================================
def admin_requerido(function):
    """
    Decorador que comprueba que el usuario esté logueado Y sea staff (admin).
    Si no es staff, lo redirige al 'home'.
    Si no está logueado, lo redirige al 'login'.
    """
    return user_passes_test(
        lambda u: u.is_authenticated and u.is_staff,
        login_url='login', # Si no está logueado, va al login
        redirect_field_name=None
    )(function)

# ===============================================
# VISTA PRINCIPAL DEL PANEL
# ===============================================
@admin_requerido
def dashboard_home(request):
    # Por ahora, redirigimos a la lista de productos
    return redirect('dashboard_productos')

# ===============================================
# VISTAS DEL PANEL DE PRODUCTOS (CRUD)
# ===============================================

@admin_requerido
def producto_list(request):
    productos = Producto.objects.all()
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
# ¡NUEVO! VISTAS DE GESTIÓN DE USUARIOS
# ===============================================

@admin_requerido
def user_list(request):
    """Muestra todos los usuarios (admins y clientes)"""
    # Usamos el modelo User de Django porque es la fuente de verdad
    usuarios = User.objects.all().order_by('username')
    context = {
        'usuarios': usuarios
    }
    return render(request, 'dashboard/user_list.html', context)

@admin_requerido
def user_toggle_staff(request, user_id):
    """Promueve o degrada a un usuario a/de admin"""
    if request.user.id == user_id:
        messages.error(request, "No puedes cambiar tu propio estado de administrador.")
        return redirect('dashboard_usuarios')
        
    user = get_object_or_404(User, id=user_id)
    # Invierte el estado de 'is_staff'
    user.is_staff = not user.is_staff
    user.save()
    
    if user.is_staff:
        messages.success(request, f"'{user.username}' ha sido promovido a Administrador.")
    else:
        messages.success(request, f"'{user.username}' ha sido degradado a Usuario normal.")
        
    return redirect('dashboard_usuarios')

@admin_requerido
def user_delete(request, user_id):
    """Elimina un usuario (y su cliente enlazado)"""
    if request.user.id == user_id:
        messages.error(request, "No puedes eliminarte a ti mismo.")
        return redirect('dashboard_usuarios')
        
    user = get_object_or_404(User, id=user_id)
    username = user.username
    user.delete() # Esto borrará el User y (por 'on_delete=models.CASCADE') el Cliente
    
    messages.success(request, f"El usuario '{username}' ha sido eliminado permanentemente.")
    return redirect('dashboard_usuarios')