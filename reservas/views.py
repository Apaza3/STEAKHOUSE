from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from .models import Reserva
from .forms import ReservaForm
from core.utils import enviar_email_automatico # ¡Tu función de email!

# --- Librerías para generar el QR ---
import qrcode
import io
import base64

# ===============================================
# VISTA DEL FORMULARIO DE RESERVA
# ===============================================
def reservation_view(request):
    if request.method == 'POST':
        form = ReservaForm(request.POST)
        if form.is_valid():
            reserva = form.save(commit=False)
            
            # Lógica de redirección basada en el tipo de pago
            if reserva.tipo_pago == 'SOLO_MESA':
                reserva.estado = 'CONFIRMADA'
                reserva.save()
                
                # ¡ENVIAR CORREO DE CONFIRMACIÓN!
                try:
                    enviar_email_automatico(
                        asunto='¡Tu reserva en The Steakhouse está confirmada!',
                        template_path='emails/confirmacion_reserva.html',
                        context_datos={'reserva': reserva, 'cliente': reserva.cliente},
                        email_destino=reserva.cliente.email
                    )
                    messages.success(request, '¡Reserva confirmada! Se ha enviado un correo con los detalles.')
                except Exception as e:
                    messages.warning(request, f'Reserva confirmada, pero no se pudo enviar el correo: {e}')
                
                return redirect('home')

            elif reserva.tipo_pago == 'PAGO_ADELANTADO':
                reserva.estado = 'PENDIENTE'
                reserva.save()
                # Redirige a la vista de espera de QR
                return redirect('payment_waiting_view', reserva_id=reserva.id)

            elif reserva.tipo_pago == 'TARJETA':
                reserva.estado = 'PENDIENTE'
                reserva.save()
                # Redirige a la NUEVA vista de pago con tarjeta
                return redirect('payment_tarjeta_view', reserva_id=reserva.id)
            
    else:
        form = ReservaForm()

    return render(request, 'reservas.html', {'form': form})

# ===============================================
# VISTAS DE SIMULACIÓN DE PAGO (QR)
# ===============================================

# 1. VISTA DE ESPERA DE PAGO (PARA LA PC)
def payment_waiting_view(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id)
    
    # Construye la URL que irá dentro del QR
    confirm_url = request.build_absolute_uri(
        reverse('payment_confirm_view', args=[reserva.id])
    )
    
    # Genera la imagen del QR en memoria
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(confirm_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convierte la imagen a formato Base64 para pasarla al HTML
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    qr_image_base64 = base64.b64encode(buffered.getvalue()).decode()
    
    context = {
        'reserva': reserva,
        'qr_image': qr_image_base64,
        'check_status_url': reverse('check_reservation_status_view', args=[reserva.id])
    }
    return render(request, 'payment_waiting.html', context)


# 2. VISTA PARA EL CELULAR (EL "COMANDO" DE PAGO)
def payment_confirm_view(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id)
    
    if reserva.estado == 'PENDIENTE':
        reserva.estado = 'CONFIRMADA'
        reserva.save()
        
        # ¡ACCIÓN CLAVE 2! Enviar el email de confirmación AHORA
        try:
            enviar_email_automatico(
                asunto='¡Pago Confirmado! Tu reserva en The Steakhouse está lista.',
                template_path='emails/confirmacion_reserva.html',
                context_datos={'reserva': reserva, 'cliente': reserva.cliente},
                email_destino=reserva.cliente.email
            )
        except Exception as e:
            print(f"Error al enviar email de confirmación QR: {e}")

    return HttpResponse("<h1>¡Pago Simulado Exitosamente!</h1><p>Tu reserva está confirmada. Puedes cerrar esta ventana.</p>")


# 3. VISTA API PARA POLLING (EL "SONDEO" DE JAVASCRIPT)
def check_reservation_status_view(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id)
    return JsonResponse({'status': reserva.estado}) # Devuelve 'PENDIENTE' o 'CONFIRMADA'

# ===============================================
# VISTAS DE SIMULACIÓN DE PAGO (TARJETA)
# ===============================================

def payment_tarjeta_view(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id)
    return render(request, 'pago_tarjeta.html', {'reserva': reserva})

def payment_tarjeta_confirm(request, reserva_id):
    # Esta vista sería llamada por el formulario de la tarjeta
    reserva = get_object_or_404(Reserva, id=reserva_id)
    
    if reserva.estado == 'PENDIENTE':
        # (Aquí iría la lógica de validación de la tarjeta con una API real)
        
        # Si el pago es exitoso:
        reserva.estado = 'CONFIRMADA'
        reserva.save()
        
        try:
            enviar_email_automatico(
                asunto='¡Pago Aceptado! Tu reserva en The Steakhouse está lista.',
                template_path='emails/confirmacion_reserva.html',
                context_datos={'reserva': reserva, 'cliente': reserva.cliente},
                email_destino=reserva.cliente.email
            )
            messages.success(request, '¡Pago aceptado y reserva confirmada! Se ha enviado un correo.')
        except Exception as e:
            messages.warning(request, f'Pago aceptado, pero no se pudo enviar el correo: {e}')

    return redirect('home')