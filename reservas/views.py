from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from .models import Reserva, Mesa
from clientes.models import Cliente # Importamos Cliente
from .forms import ReservaForm
from core.utils import enviar_email_automatico
from django.contrib.auth.decorators import login_required # ¡IMPORTANTE!

import qrcode
import io
import base64

# ===============================================
# VISTA DEL FORMULARIO DE RESERVA
# ===============================================
@login_required(login_url='login') # ¡PROTEGIDA!
def reservation_view(request):
    
    # Intentamos encontrar el cliente enlazado al usuario
    try:
        cliente_actual = Cliente.objects.get(usuario=request.user)
    except Cliente.DoesNotExist:
        messages.error(request, 'Error: Tu usuario no está enlazado a un perfil de cliente.')
        return redirect('home')
        
    if request.method == 'POST':
        form = ReservaForm(request.POST)
        if form.is_valid():
            reserva = form.save(commit=False)
            
            # Asignamos el cliente automáticamente
            reserva.cliente = cliente_actual 
            
            if reserva.tipo_pago == 'SOLO_MESA':
                reserva.estado = 'CONFIRMADA'
                reserva.save()
                
                try:
                    enviar_email_automatico(
                        '¡Tu reserva en The Steakhouse está confirmada!',
                        'emails/confirmacion_reserva.html',
                        {'reserva': reserva, 'cliente': reserva.cliente},
                        reserva.cliente.email
                    )
                    messages.success(request, '¡Reserva confirmada! Se ha enviado un correo con los detalles.')
                except Exception as e:
                    messages.warning(request, f'Reserva confirmada, pero no se pudo enviar el correo: {e}')
                
                return redirect('home')

            elif reserva.tipo_pago == 'PAGO_ADELANTADO':
                reserva.estado = 'PENDIENTE'
                reserva.save()
                return redirect('payment_waiting', reserva_id=reserva.id)

            elif reserva.tipo_pago == 'TARJETA':
                reserva.estado = 'PENDIENTE'
                reserva.save()
                return redirect('payment_tarjeta', reserva_id=reserva.id)
            
    else:
        # Pre-llenamos el formulario con el cliente
        form = ReservaForm(initial={'cliente': cliente_actual})

    # Pasamos las mesas disponibles al formulario
    mesas_disponibles = Mesa.objects.filter(estado='DISPONIBLE')
    form.fields['mesa'].queryset = mesas_disponibles
    
    return render(request, 'reservas.html', {'form': form})

# ===============================================
# VISTAS DE SIMULACIÓN DE PAGO
# ===============================================

@login_required(login_url='login')
def payment_waiting_view(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id, cliente__usuario=request.user)
    
    confirm_url = request.build_absolute_uri(
        reverse('payment_confirm', args=[reserva.id])
    )
    
    # Generar QR
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(confirm_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    qr_image_base64 = base64.b64encode(buffered.getvalue()).decode()
    
    context = {
        'reserva': reserva,
        'qr_image': qr_image_base64,
        'check_status_url': reverse('check_reservation_status', args=[reserva.id])
    }
    return render(request, 'payment_waiting.html', context)

# (Esta vista no necesita login, ya que la URL es secreta)
def payment_confirm_view(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id)
    
    if reserva.estado == 'PENDIENTE':
        reserva.estado_pago = 'PAGADO' # (Nota: este campo ya no existe, pero lo mantenemos por si acaso)
        reserva.estado = 'CONFIRMADA'
        reserva.save()
        
        try:
            enviar_email_automatico(
                '¡Pago Confirmado! Tu reserva en The Steakhouse está lista.',
                'emails/confirmacion_reserva.html',
                {'reserva': reserva, 'cliente': reserva.cliente},
                reserva.cliente.email
            )
        except Exception as e:
            print(f"Error al enviar email de confirmación de pago: {e}")

    return HttpResponse("<h1>¡Pago Simulado Exitosamente!</h1><p>Tu reserva está confirmada. Puedes cerrar esta ventana.</p>")

@login_required(login_url='login')
def check_reservation_status_view(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id, cliente__usuario=request.user)
    return JsonResponse({'status': reserva.estado})

# === VISTAS PARA TARJETA ===

@login_required(login_url='login')
def payment_tarjeta_view(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id, cliente__usuario=request.user)
    return render(request, 'pago_tarjeta.html', {'reserva': reserva})

@login_required(login_url='login')
def payment_tarjeta_confirm(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id, cliente__usuario=request.user)
    
    if reserva.estado == 'PENDIENTE':
        reserva.estado = 'CONFIRMADA'
        reserva.save()
        
        try:
            enviar_email_automatico(
                '¡Pago Confirmado! Tu reserva en The Steakhouse está lista.',
                'emails/confirmacion_reserva.html',
                {'reserva': reserva, 'cliente': reserva.cliente},
                reserva.cliente.email
            )
            messages.success(request, '¡Pago aceptado y reserva confirmada! Se ha enviado un correo.')
        except Exception as e:
            messages.warning(request, f'Pago aceptado, pero no se pudo enviar el correo: {e}')

    return redirect('home')