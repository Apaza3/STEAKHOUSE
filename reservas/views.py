from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from datetime import datetime, timedelta, date
import json

# Modelos y Forms
from .models import Reserva, Mesa
from clientes.models import Cliente 
from .forms import ReservaForm
from core.utils import enviar_email_automatico

# Imports para QR
import qrcode
import io
import base64

# ======================================================
# VISTA PRINCIPAL DE RESERVA (FORMULARIO + LOGICA)
# ======================================================
@login_required(login_url='login') 
def reservation_view(request):
    
    try:
        cliente_actual = request.user.cliente
    except Cliente.DoesNotExist:
        messages.error(request, 'Tu cuenta de usuario no tiene un perfil de cliente asociado.')
        return redirect('home')
            
    # Valores iniciales para mostrar en el formulario
    initial_data = {
        'cliente': cliente_actual,
        'fecha_reserva': date.today(),
        'hora_reserva': datetime.now().strftime('%H:00'),
        'numero_personas': 2
    }

    # Lógica para procesar el formulario (POST)
    if request.method == 'POST':
        form = ReservaForm(request.POST)
        
        if form.is_valid():
            # Obtenemos datos limpios
            mesa_id = form.cleaned_data['mesa_id'] # Este ID viene del click visual
            fecha = form.cleaned_data['fecha_reserva']
            hora = form.cleaned_data['hora_reserva']
            duracion = int(form.cleaned_data['duracion_horas'])
            
            # Validar que la mesa existe y sigue libre (Doble check de seguridad)
            mesa = get_object_or_404(Mesa, id=mesa_id)
            
            # Calcular horarios para validar conflicto
            inicio_dt = datetime.combine(fecha, hora)
            fin_dt = inicio_dt + timedelta(hours=duracion)
            hora_fin = fin_dt.time()
            
            # Verificar si realmente está libre (por si otro usuario la ganó)
            conflicto = Reserva.objects.filter(
                mesa=mesa,
                fecha_reserva=fecha,
                estado__in=['CONFIRMADA', 'PENDIENTE']
            ).filter(
                hora_reserva__lt=hora_fin,
                hora_fin__gt=hora
            ).exists()

            if conflicto:
                messages.error(request, f'Lo sentimos, la Mesa {mesa.numero} ya fue reservada por otro cliente en ese horario.')
                # CORREGIDO: Apunta a 'reservas.html' directo en templates/
                return render(request, 'reservas.html', {'form': form, 'cliente': cliente_actual})

            # Crear Reserva
            reserva = form.save(commit=False)
            reserva.cliente = cliente_actual
            reserva.mesa = mesa
            # (hora_fin se calcula en el save() del modelo)
            
            # Lógica de Pago
            if reserva.tipo_pago in ['PAGO_ADELANTADO', 'TARJETA']:
                reserva.estado = 'PENDIENTE'
                reserva.monto_pagado = 30.00
                reserva.save()
                
                if reserva.tipo_pago == 'PAGO_ADELANTADO':
                    return redirect('payment_waiting_view', reserva_id=reserva.id)
                else:
                    return redirect('payment_tarjeta_view', reserva_id=reserva.id)
            else:
                reserva.estado = 'CONFIRMADA'
                reserva.save()
                
                # Email
                try:
                    enviar_email_automatico(
                        template_path='emails/confirmacion_reserva.html',
                        context_datos={'reserva': reserva, 'cliente': reserva.cliente},
                        asunto='¡Reserva Confirmada! - The Steakhouse',
                        email_destino=reserva.cliente.email
                    )
                except Exception as e:
                    print(f"Error email: {e}")
                
                messages.success(request, f'¡Reserva confirmada para la Mesa {mesa.numero}!')
                return redirect('home')

        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    
    else:
        form = ReservaForm(initial=initial_data)

    # ---------------------------------------------------------
    # PRE-CARGAR TODAS LAS MESAS PARA LA VISTA VISUAL
    # ---------------------------------------------------------
    todas_las_mesas = Mesa.objects.all().order_by('numero')
    
    # CORREGIDO: Apunta a 'reservas.html' directo en templates/
    return render(request, 'reservas.html', {
        'form': form, 
        'cliente': cliente_actual,
        'mesas_list': todas_las_mesas 
    })


# ======================================================
# API JSON (NECESARIA PARA LA INTERACTIVIDAD)
# ======================================================
@login_required
def api_mesas_disponibles(request):
    fecha_str = request.GET.get('fecha')
    hora_str = request.GET.get('hora')
    duracion = int(request.GET.get('duracion', 2))

    if not fecha_str or not hora_str:
        return JsonResponse({'mesas': []}) 

    try:
        fecha_dt = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        hora_dt = datetime.strptime(hora_str, '%H:%M').time()
        
        inicio_dt = datetime.combine(fecha_dt, hora_dt)
        fin_dt = inicio_dt + timedelta(hours=duracion)
        hora_fin_dt = fin_dt.time()

        reservas_conflicto = Reserva.objects.filter(
            fecha_reserva=fecha_dt,
            estado__in=['CONFIRMADA', 'PENDIENTE']
        ).filter(
            hora_reserva__lt=hora_fin_dt,
            hora_fin__gt=hora_dt
        )
        
        ids_ocupados = list(reservas_conflicto.values_list('mesa_id', flat=True))
        
        mesas = Mesa.objects.all().values('id', 'numero', 'capacidad', 'tipo')
        
        data = []
        for m in mesas:
            estado = 'OCUPADA' if m['id'] in ids_ocupados else 'LIBRE'
            data.append({
                'id': m['id'],
                'numero': m['numero'],
                'capacidad': m['capacidad'],
                'tipo': m.get('tipo', 'Normal'), 
                'estado': estado
            })
            
        return JsonResponse({'mesas': data})

    except ValueError:
        return JsonResponse({'error': 'Datos inválidos'}, status=400)


# ======================================================
# VISTAS DE PAGO (RUTAS CORREGIDAS)
# ======================================================

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
    # CORREGIDO: Apunta a 'payment_waiting.html' directo en templates/
    return render(request, 'payment_waiting.html', context)

@login_required(login_url='login')
def payment_confirm_view(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id)
    
    if reserva.estado == 'PENDIENTE':
        reserva.estado = 'CONFIRMADA'
        reserva.monto_pagado = 30.00
        reserva.save()
        
        try:
            enviar_email_automatico(
                 template_path='emails/confirmacion_reserva.html',
                 context_datos={'reserva': reserva, 'cliente': reserva.cliente},
                 asunto='¡Pago Recibido! Reserva Confirmada.',
                 email_destino=reserva.cliente.email
            )
        except Exception:
            pass

    html_response = """
    <html lang="es" data-bs-theme="dark">
    <head>
        <meta charset="UTF-8">
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
                <p class="lead">Tu reserva ha sido confirmada.</p>
                <p class="text-muted">Puedes cerrar esta ventana.</p>
            </div>
        </div>
    </body>
    </html>
    """
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
    # CORREGIDO: Apunta a 'pago_tarjeta.html' directo en templates/
    return render(request, 'pago_tarjeta.html', context)

@login_required(login_url='login')
def payment_tarjeta_confirm(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id, cliente__usuario=request.user)
    
    if reserva.estado == 'PENDIENTE':
        reserva.estado = 'CONFIRMADA'
        reserva.monto_pagado = 30.00
        reserva.save()
        
        try:
            enviar_email_automatico(
                template_path='emails/confirmacion_reserva.html',
                context_datos={'reserva': reserva, 'cliente': reserva.cliente},
                asunto='¡Pago con Tarjeta Exitoso!',
                email_destino=reserva.cliente.email
            )
            messages.success(request, '¡Pago aceptado y reserva confirmada!')
        except Exception as e:
            messages.warning(request, f'Pago aceptado, pero error al enviar email: {e}')

    return redirect('home')