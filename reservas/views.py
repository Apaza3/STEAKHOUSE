from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from .models import Reserva, Mesa
from clientes.models import Cliente 
from .forms import ReservaForm
from core.utils import enviar_email_automatico
from django.contrib.auth.decorators import login_required

import qrcode
import io
import base64
from datetime import datetime, timedelta
from django.db.models import Q


# ===============================================
# VISTA DEL FORMULARIO DE RESERVA (¡CORREGIDA!)
# ===============================================
@login_required(login_url='login') 
def reservation_view(request):
    
    try:
        cliente_actual = request.user.cliente
    except Cliente.DoesNotExist:
        messages.error(request, 'Las cuentas de Administrador no pueden hacer reservas. Por favor, usa una cuenta de cliente.')
        return redirect('home')
            
    if request.method == 'POST':
        form = ReservaForm(request.POST)
        
        if form.is_valid():
            fecha = form.cleaned_data['fecha_reserva']
            hora_inicio = form.cleaned_data['hora_reserva']
            duracion = int(form.cleaned_data['duracion_horas'])
            personas = form.cleaned_data['numero_personas']
            
            try:
                inicio_dt = datetime.combine(fecha, hora_inicio)
                fin_dt = inicio_dt + timedelta(hours=duracion)
                hora_fin = fin_dt.time()
            except Exception as e:
                messages.error(request, f"Error al calcular la hora: {e}")
                return render(request, 'reservas.html', {'form': form, 'cliente_actual': cliente_actual})

            reservas_en_conflicto = Reserva.objects.filter(
                fecha_reserva=fecha,
                estado__in=['CONFIRMADA', 'PENDIENTE']
            ).filter(
                Q(hora_reserva__lt=hora_fin) & Q(hora_fin__gt=hora_inicio)
            )
            
            mesas_ocupadas_ids = reservas_en_conflicto.values_list('mesa_id', flat=True)

            mesa_disponible = Mesa.objects.filter(
                estado='DISPONIBLE',
                capacidad__gte=personas
            ).exclude(
                id__in=mesas_ocupadas_ids
            ).order_by('capacidad').first()

            if mesa_disponible:
                reserva = form.save(commit=False)
                reserva.cliente = cliente_actual
                reserva.mesa = mesa_disponible
                
                if reserva.tipo_pago == 'PAGO_ADELANTADO' or reserva.tipo_pago == 'TARJETA':
                    reserva.estado = 'PENDIENTE'
                    reserva.monto_pagado = 30.00
                    reserva.save()
                    
                    if reserva.tipo_pago == 'PAGO_ADELANTADO':
                        return redirect('payment_waiting_view', reserva_id=reserva.id)
                    else:
                        return redirect('payment_tarjeta_view', reserva_id=reserva.id)
                
                else: # 'SOLO_MESA'
                    reserva.estado = 'CONFIRMADA'
                    reserva.monto_pagado = 0.00
                    reserva.save()
                    
                    try:
                        # ===================================================
                        # ¡LLAMADA CORREGIDA! (Argumentos en orden)
                        # ===================================================
                        enviar_email_automatico(
                            template_path='emails/confirmacion_reserva.html',
                            context_datos={'reserva': reserva, 'cliente': reserva.cliente},
                            asunto='¡Tu reserva en The Steakhouse está confirmada!',
                            email_destino=reserva.cliente.email
                        )
                        messages.success(request, f'¡Reserva confirmada para la Mesa {reserva.mesa.numero}! Se ha enviado un correo con los detalles.')
                    except Exception as e:
                        # (La función 'enviar_email' ya imprime el error, pero por si acaso)
                        messages.warning(request, f'Reserva confirmada (Mesa {reserva.mesa.numero}), pero no se pudo enviar el correo: {e}')
                    
                    return redirect('home')

            else:
                messages.error(request, f'Lo sentimos, no hay mesas disponibles para {personas} personas en esa fecha y hora. Por favor, intenta otro horario.')
                return render(request, 'reservas.html', {'form': form, 'cliente_actual': cliente_actual})

        else:
            messages.error(request, 'El formulario tiene errores. Por favor, revisa los campos.')
            
    else: 
        form = ReservaForm(initial={'cliente': cliente_actual})

    context = {
        'form': form,
        'cliente_actual': cliente_actual 
    }
    
    return render(request, 'reservas.html', context)


# ===============================================
# VISTAS DE SIMULACIÓN DE PAGO (¡CORREGIDAS!)
# ===============================================

@login_required(login_url='login')
def payment_waiting_view(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id, cliente__usuario=request.user)
    
    confirm_url = request.build_absolute_uri(
        reverse('payment_confirm_view', args=[reserva.id]) 
    )
    
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
        'check_status_url': reverse('check_reservation_status_view', args=[reserva.id]),
        'monto_a_pagar': 30
    }
    return render(request, 'payment_waiting.html', context)

def payment_confirm_view(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id)
    
    if reserva.estado == 'PENDIENTE':
        reserva.estado = 'CONFIRMADA'
        reserva.monto_pagado = 30.00
        reserva.save()
        
        try:
            # ===================================================
            # ¡LLAMADA CORREGIDA! (Argumentos en orden)
            # ===================================================
            enviar_email_automatico(
                template_path='emails/confirmacion_reserva.html',
                context_datos={'reserva': reserva, 'cliente': reserva.cliente},
                asunto='¡Pago Confirmado! Tu reserva en The Steakhouse está lista.',
                email_destino=reserva.cliente.email
            )
        except Exception as e:
            print(f"Error al enviar email de confirmación de pago: {e}")

    html_response = """
    <html lang="es" data-bs-theme="dark">
    <head>
        <meta charset="UTF-g">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Pago Confirmado</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body { background-color: #1a1a1a; color: #f4f0e8; display: grid; place-items: center; min-height: 100vh; }
            .card { background-color: #2c2c2c; border: 1px solid #c89b3f; }
            .icon { font-size: 5rem; color: #28a745; }
        </style>
    </head>
    <body>
        <div class="card text-center shadow-lg" style="width: 90%; max-width: 400px;">
            <div class="card-body p-5">
                <div class="icon mb-3">✓</div>
                <h1 class="h3">¡Pago Exitoso!</h1>
                <p class="lead">Tu reserva (ID: ...{reserva_id_corta}) ha sido confirmada.</p>
                <p class="text-muted">Ya puedes cerrar esta ventana.</p>
            </div>
        </div>
    </body>
    </html>
    """.replace("{reserva_id_corta}", str(reserva_id)[-12:])
    return HttpResponse(html_response)

@login_required(login_url='login')
def check_reservation_status_view(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id, cliente__usuario=request.user)
    return JsonResponse({'status': reserva.estado})

@login_required(login_url='login')
def payment_tarjeta_view(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id, cliente__usuario=request.user)
    context = {
        'reserva': reserva,
        'monto_a_pagar': 30
    }
    return render(request, 'pago_tarjeta.html', context)

@login_required(login_url='login')
def payment_tarjeta_confirm(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id, cliente__usuario=request.user)
    
    if reserva.estado == 'PENDIENTE':
        reserva.estado = 'CONFIRMADA'
        reserva.monto_pagado = 30.00
        reserva.save()
        
        try:
            # ===================================================
            # ¡LLAMADA CORREGIDA! (Argumentos en orden)
            # ===================================================
            enviar_email_automatico(
                template_path='emails/confirmacion_reserva.html',
                context_datos={'reserva': reserva, 'cliente': reserva.cliente},
                asunto='¡Pago Confirmado! Tu reserva en The Steakhouse está lista.',
                email_destino=reserva.cliente.email
            )
            messages.success(request, '¡Pago aceptado y reserva confirmada! Se ha enviado un correo.')
        except Exception as e:
            messages.warning(request, f'Pago aceptado, pero no se pudo enviar el correo: {e}')

    return redirect('home')