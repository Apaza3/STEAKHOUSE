from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from django.urls import reverse_lazy
from .forms import ClienteRegistrationForm

# ===============================================
# VISTA DE REGISTRO
# ===============================================
def register_view(request):
    if request.method == 'POST':
        form = ClienteRegistrationForm(request.POST)
        if form.is_valid():
            cliente = form.save()
            
            # Iniciar sesión automáticamente al nuevo usuario
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
        # Redirigir a /admin/ si es staff, o a / (home) si es cliente
        if self.request.user.is_staff:
            return reverse_lazy('admin:index')
        return reverse_lazy('home')

    def form_invalid(self, form):
        messages.error(self.request, 'Usuario o contraseña incorrectos. Inténtalo de nuevo.')
        return super().form_invalid(form)

# ===============================================
# VISTA DE LOGOUT
# ===============================================
class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('home') # A dónde ir después de salir

    def dispatch(self, request, *args, **kwargs):
        messages.success(request, 'Has cerrado sesión exitosamente.')
        return super().dispatch(request, *args, **kwargs)