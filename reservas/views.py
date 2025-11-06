from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from .models import Reserva, Mesa
from core.utils import enviar_email_automatico # Importamos tu función de email

# --- Librerías para generar el QR ---
import qrcode
import io
import base64

# ===============================================
# VISTA DEL FORMULARIO DE RESERVA
# ===============================================
def reservation_view(request):
    
    if request.method == 'POST':
        # 1. Obtenemos los datos del formulario
        nombre = request.POST.get('nombre')
        email = request.POST.get('email')
        fecha = request.POST.get('fecha')
        hora = request.POST.get('hora')
        personas = request.POST.get('personas')
        tipo_reserva = request.POST.get('tipo_reserva') # 'MESA' o 'PAGO'
        
        try:
            # 2. Creamos y guardamos la reserva en la base de datos
            nueva_reserva = Reserva.objects.create(
                nombre_cliente=nombre,
                email_cliente=email,
                fecha=fecha,
                hora=hora,
                cant_personas=personas,
                tipo_reserva=tipo_reserva,
                estado_reserva='PENDIENTE', 
                estado_pago='PENDIENTE'    
            )
            
            # 3. Verificamos el tipo de reserva
            if tipo_reserva == 'PAGO':
                # ¡Simulación QR! Redirigimos a la página de espera de pago
                return redirect('payment_waiting', id_reserva=nueva_reserva.id_reserva)
            
            else: # tipo_reserva == 'MESA'
                # Era "Solo Mesa". Aprobamos y enviamos email de confirmación
                nueva_reserva.estado_reserva = 'CONFIRMADA'
                nueva_reserva.save()
                
                context_email = {
                    'nombre_cliente': nueva_reserva.nombre_cliente,
                    'fecha': nueva_reserva.fecha,
                    'hora': nueva_reserva.hora,
                    'personas': nueva_reserva.cant_personas,
                }
                
                enviar_email_automatico(
                    template_path='emails/confirmacion.html',
                    context_datos=context_email,
                    asunto='¡Confirmación de Reserva en The Steakhouse!',
                    email_destino=nueva_reserva.email_cliente
                )

                messages.success(request, '¡Reserva de mesa confirmada! Revisa tu correo.')
                return redirect('home')

        except Exception as e:
            print(f"Error al crear reserva: {e}")
            messages.error(request, f'Error al procesar la reserva: {e}. Inténtalo de nuevo.')
            return redirect('reservas_page')

    else:
        return render(request, 'reservas.html', {})

# ===============================================
# VISTAS DE SIMULACIÓN DE PAGO
# ===============================================

# 1. VISTA DE ESPERA DE PAGO (PARA LA PC)
def payment_waiting_view(request, id_reserva):
    try:
        reserva = get_object_or_404(Reserva, id_reserva=id_reserva)
        
        # Construye la URL que irá dentro del QR
        confirm_url = request.build_absolute_uri(
            reverse('payment_confirm', args=[reserva.id_reserva])
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
            'check_status_url': reverse('check_reservation_status', args=[reserva.id_reserva])
        }
        return render(request, 'payment_waiting.html', context)
    except Exception as e:
        print(f"Error al generar QR: {e}")
        messages.error(request, 'Error al generar el QR. Intente de nuevo.')
        return redirect('reservas_page')


# 2. VISTA PARA EL CELULAR (EL "COMANDO" DE PAGO)
def payment_confirm_view(request, id_reserva):
    try:
        reserva = get_object_or_404(Reserva, id_reserva=id_reserva)
        
        if reserva.estado_pago == 'PENDIENTE':
            # ¡LA ACCIÓN CLAVE!
            reserva.estado_pago = 'PAGADO'
            reserva.estado_reserva = 'CONFIRMADA'
            reserva.save()
            
            # ¡ACCIÓN CLAVE 2! Enviar el email de confirmación AHORA
            context_email = {
                'nombre_cliente': reserva.nombre_cliente,
                'fecha': reserva.fecha,
                'hora': reserva.hora,
                'personas': reserva.cant_personas,
            }
            enviar_email_automatico(
                template_path='emails/confirmacion.html',
                context_datos=context_email,
                asunto='¡Pago Confirmado! Tu reserva en The Steakhouse está lista.',
                email_destino=reserva.email_cliente
            )

        return HttpResponse("<h1>¡Pago Simulado Exitosamente!</h1><p>Tu reserva está confirmada. Puedes cerrar esta ventana.</p>")
    
    except Exception as e:
        return HttpResponse(f"<h1>Error</h1><p>No se pudo procesar el pago: {e}</p>")


# 3. VISTA API PARA POLLING (EL "SONDEO" DE JAVASCRIPT)
def check_reservation_status_view(request, id_reserva):
    try:
        reserva = get_object_or_404(Reserva, id_reserva=id_reserva)
        return JsonResponse({'status': reserva.estado_pago}) 
    except:
        return JsonResponse({'status': 'ERROR'}, status=404)