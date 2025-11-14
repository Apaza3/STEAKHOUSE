from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.contrib import messages
from django.urls import reverse_lazy
from .forms import ClienteRegistrationForm, ClienteEditForm
from django.contrib.auth.decorators import login_required
from .models import Cliente
from reservas.models import Reserva # <-- ¡NUEVA IMPORTACIÓN!
from django.utils import timezone   # <-- ¡NUEVA IMPORTACIÓN!
from datetime import datetime       # <-- ¡NUEVA IMPORTACIÓN!

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

# ===================================================
# ¡NUEVO! LÓGICA DE REEMBOLSO (para las vistas de abajo)
# ===================================================
def _calcular_reembolso(reserva, ahora):
    """
    Calcula el monto de reembolso y el mensaje según las reglas de negocio.
    """
    # Si no pagó o no está confirmada, no hay reembolso
    if reserva.monto_pagado <= 0 or reserva.estado not in ['CONFIRMADA', 'PENDIENTE']:
        return {'monto': 0, 'mensaje': 'Esta reserva no es reembolsable.'}

    # 1. Regla: 20 minutos después de crearla (Reembolso completo)
    if reserva.created_at:
        tiempo_desde_creacion = ahora - reserva.created_at
        if tiempo_desde_creacion.total_seconds() <= 1200: # 20 minutos
            return {'monto': 30.00, 'mensaje': 'Reembolso completo de 30 Bs (cancelación rápida dentro de los 20 min).'}

    # 2. Regla: Tiempo ANTES de la reserva
    # Combinamos la fecha y hora de la reserva en un objeto datetime con zona horaria
    inicio_reserva_dt = timezone.make_aware(datetime.combine(reserva.fecha_reserva, reserva.hora_reserva))
    tiempo_para_reserva = inicio_reserva_dt - ahora
    
    # Si la reserva ya pasó, no hay reembolso
    if tiempo_para_reserva.total_seconds() < 0:
        return {'monto': 0, 'mensaje': 'Esta reserva ya pasó. No es reembolsable.'}

    # Si cancela 1 hora antes
    if tiempo_para_reserva.total_seconds() >= 3600: # 1 hora
        return {'monto': 15.00, 'mensaje': 'Reembolso parcial de 15 Bs (cancelación 1 hora antes).'}
    
    # Si cancela 30 minutos antes
    if tiempo_para_reserva.total_seconds() >= 1800: # 30 minutos
        return {'monto': 10.00, 'mensaje': 'Reembolso parcial de 10 Bs (cancelación 30 min antes).'}

    # Si falta menos de 30 minutos
    return {'monto': 0, 'mensaje': 'No reembolsable (falta menos de 30 min para la reserva).'}


# ===================================================
# ¡NUEVO! VISTA "MIS RESERVAS"
# ===================================================
@login_required
def mis_reservas_view(request):
    try:
        cliente = request.user.cliente
    except Cliente.DoesNotExist:
        messages.error(request, 'No tienes un perfil de cliente.')
        return redirect('home')

    # Obtenemos todas las reservas del cliente
    reservas = Reserva.objects.filter(cliente=cliente).order_by('-fecha_reserva', '-hora_reserva')
    
    ahora = timezone.now()
    reservas_con_info = []
    
    for reserva in reservas:
        # Calculamos el reembolso para cada una
        info_reembolso = _calcular_reembolso(reserva, ahora)
        
        # Comprobamos si la reserva aún se puede cancelar
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


# ===================================================
# ¡NUEVO! VISTA "CANCELAR RESERVA"
# ===================================================
@login_required
def cancelar_reserva_view(request, reserva_id):
    # Aseguramos que la reserva exista y sea de este cliente
    reserva = get_object_or_404(Reserva, id=reserva_id, cliente__usuario=request.user)
    
    ahora = timezone.now()
    
    # Verificamos que todavía se pueda cancelar
    se_puede_cancelar = reserva.estado in ['PENDIENTE', 'CONFIRMADA'] and (timezone.make_aware(datetime.combine(reserva.fecha_reserva, reserva.hora_reserva)) > ahora)

    if not se_puede_cancelar:
        messages.error(request, 'Esta reserva ya no se puede cancelar.')
        return redirect('mis_reservas')

    if request.method == 'POST':
        # Calculamos el reembolso
        info_reembolso = _calcular_reembolso(reserva, ahora)
        
        # 1. Cambiamos el estado de la reserva
        reserva.estado = 'CANCELADA'
        # (El 'monto_pagado' lo dejamos como está, el admin gestionará el reembolso)
        reserva.save()
        
        # 2. ¡Liberamos la mesa!
        if reserva.mesa:
            reserva.mesa.estado = 'DISPONIBLE'
            reserva.mesa.save()
            
        messages.success(request, f'Reserva cancelada. {info_reembolso["mensaje"]}')
        return redirect('mis_reservas')
    
    # Si es GET, simplemente redirige (no deberíamos llegar aquí)
    return redirect('mis_reservas')