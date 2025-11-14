from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
# ¡AÑADIDO PasswordChangeView!
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.contrib import messages
from django.urls import reverse_lazy
from .forms import ClienteRegistrationForm, ClienteEditForm
from django.contrib.auth.decorators import login_required
from .models import Cliente

# ===============================================
# VISTA DE REGISTRO
# ===============================================
def register_view(request):
    if request.method == 'POST':
        form = ClienteRegistrationForm(request.POST)
        if form.is_valid():
            cliente = form.save()
            cliente.usuario.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, cliente.usuario)
            messages.success(request, f'¡Bienvenido, {cliente.nombre}! Tu cuenta ha sido creada.')
            return redirect('home')
    else:
        form = ClienteRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

# ===============================================
# VISTA DE LOGIN
# ===============================================
class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    
    def get_success_url(self):
        if self.request.user.is_staff:
            return reverse_lazy('dashboard_home')
        return reverse_lazy('home')

    def form_invalid(self, form):
        messages.error(self.request, 'Usuario o contraseña incorrectos. Inténtalo de nuevo.')
        return super().form_invalid(form)

# ===============================================
# VISTA DE LOGOUT
# ===============================================
class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('home')

    def dispatch(self, request, *args, **kwargs):
        messages.success(request, 'Has cerrado sesión exitosamente.')
        return super().dispatch(request, *args, **kwargs)

# ===============================================
# VISTA DE PERFIL DE CLIENTE
# ===============================================
@login_required
def perfil_view(request):
    try:
        cliente = request.user.cliente
    except Cliente.DoesNotExist:
        messages.error(request, 'No tienes un perfil de cliente para editar.')
        return redirect('home')
        
    if request.method == 'POST':
        form = ClienteEditForm(request.POST, instance=cliente, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Tu perfil ha sido actualizado exitosamente!')
            return redirect('perfil')
        else:
            messages.error(request, 'Por favor, corrige los errores en el formulario.')
    else:
        form = ClienteEditForm(instance=cliente, user=request.user)
        
    context = {
        'form': form
    }
    return render(request, 'registration/perfil.html', context)

# ===================================================
# ¡NUEVO! VISTA PARA CAMBIAR CONTRASEÑA
# ===================================================
class CustomPasswordChangeView(PasswordChangeView):
    # Usaremos un template nuevo que vamos a crear
    template_name = 'registration/password_change.html'
    # Cuando termine, volvemos a la página de perfil
    success_url = reverse_lazy('perfil')

    def form_valid(self, form):
        # Añadimos un mensaje de éxito
        messages.success(self.request, '¡Tu contraseña ha sido cambiada exitosamente!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Error al cambiar la contraseña. Por favor, revisa los campos.')
        return super().form_invalid(form)