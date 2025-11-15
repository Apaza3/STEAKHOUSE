from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.contrib import messages
from django.urls import reverse_lazy
from .forms import ClienteRegistrationForm, ClienteEditForm
from django.contrib.auth.decorators import login_required
from .models import Cliente
from reservas.models import Reserva 
from django.utils import timezone   
from datetime import datetime       

# ... (Tu vista register_view, CustomLoginView y CustomLogoutView se quedan IGUAL) ...
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

class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    
    def get_success_url(self):
        if self.request.user.is_staff:
            return reverse_lazy('dashboard_home')
        return reverse_lazy('home')

    def form_invalid(self, form):
        messages.error(self.request, 'Usuario o contraseña incorrectos. Inténtalo de nuevo.')
        return super().form_invalid(form)

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('home')

    def dispatch(self, request, *args, **kwargs):
        messages.success(request, 'Has cerrado sesión exitosamente.')
        return super().dispatch(request, *args, **kwargs)

# ===============================================
# VISTA DE PERFIL DE CLIENTE (¡ACTUALIZADA!)
# ===============================================
@login_required
def perfil_view(request):
    try:
        cliente = request.user.cliente
    except Cliente.DoesNotExist:
        messages.error(request, 'No tienes un perfil de cliente para editar.')
        return redirect('home')
        
    if request.method == 'POST':
        # ¡CAMBIO! Añadimos request.FILES para la foto
        form = ClienteEditForm(request.POST, request.FILES, instance=cliente, user=request.user)
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
# VISTA PARA CAMBIAR CONTRASEÑA
# ===================================================
class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'registration/password_change.html'
    success_url = reverse_lazy('perfil')

    def form_valid(self, form):
        messages.success(self.request, '¡Tu contraseña ha sido cambiada exitosamente!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Error al cambiar la contraseña. Por favor, revisa los campos.')
        return super().form_invalid(form)

# ... (Tus vistas _calcular_reembolso, mis_reservas_view y cancelar_reserva_view se quedan IGUAL) ...
def _calcular_reembolso(reserva, ahora):
    """
    Calcula el monto de reembolso y el mensaje según las reglas de negocio.
    """
    if reserva.monto_pagado <= 0 or reserva.estado not in ['CONFIRMADA', 'PENDIENTE']:
        return {'monto': 0, 'mensaje': 'Esta reserva no es reembolsable.'}

    if reserva.created_at:
        tiempo_desde_creacion = ahora - reserva.created_at
        if tiempo_desde_creacion.total_seconds() <= 1200: # 20 minutos
            return {'monto': 30.00, 'mensaje': 'Reembolso completo de 30 Bs (cancelación rápida dentro de los 20 min).'}

    inicio_reserva_dt = timezone.make_aware(datetime.combine(reserva.fecha_reserva, reserva.hora_reserva))
    tiempo_para_reserva = inicio_reserva_dt - ahora
    
    if tiempo_para_reserva.total_seconds() < 0:
        return {'monto': 0, 'mensaje': 'Esta reserva ya pasó. No es reembolsable.'}

    if tiempo_para_reserva.total_seconds() >= 3600: # 1 hora
        return {'monto': 15.00, 'mensaje': 'Reembolso parcial de 15 Bs (cancelación 1 hora antes).'}
    
    if tiempo_para_reserva.total_seconds() >= 1800: # 30 minutos
        return {'monto': 10.00, 'mensaje': 'Reembolso parcial de 10 Bs (cancelación 30 min antes).'}

    return {'monto': 0, 'mensaje': 'No reembolsable (falta menos de 30 min para la reserva).'}


@login_required
def mis_reservas_view(request):
    try:
        cliente = request.user.cliente
    except Cliente.DoesNotExist:
        messages.error(request, 'No tienes un perfil de cliente.')
        return redirect('home')

    reservas = Reserva.objects.filter(cliente=cliente).order_by('-fecha_reserva', '-hora_reserva')
    
    ahora = timezone.now()
    reservas_con_info = []
    
    for reserva in reservas:
        info_reembolso = _calcular_reembolso(reserva, ahora)
        se_puede_cancelar = reserva.estado in ['PENDIENTE', 'CONFIRMADA'] and (timezone.make_aware(datetime.combine(reserva.fecha_reserva, reserva.hora_reserva)) > ahora)
        
        reservas_con_info.append({
            'reserva': reserva,
            'info_reembolso': info_reembolso,
            'se_puede_cancelar': se_puede_cancelar
        })

    context = {
        'reservas_con_info': reservas_con_info
    }
    return render(request, 'registration/mis_reservas.html', context)


@login_required
def cancelar_reserva_view(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id, cliente__usuario=request.user)
    
    ahora = timezone.now()
    
    se_puede_cancelar = reserva.estado in ['PENDIENTE', 'CONFIRMADA'] and (timezone.make_aware(datetime.combine(reserva.fecha_reserva, reserva.hora_reserva)) > ahora)

    if not se_puede_cancelar:
        messages.error(request, 'Esta reserva ya no se puede cancelar.')
        return redirect('mis_reservas')

    if request.method == 'POST':
        info_reembolso = _calcular_reembolso(reserva, ahora)
        
        reserva.estado = 'CANCELADA'
        reserva.save()
        
        if reserva.mesa:
            reserva.mesa.estado = 'DISPONIBLE'
            reserva.mesa.save()
            
        messages.success(request, f'Reserva cancelada. {info_reembolso["mensaje"]}')
        return redirect('mis_reservas')
    
    return redirect('mis_reservas')