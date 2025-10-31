from django.shortcuts import render, redirect
from django.contrib import messages  # Para enviar mensajes de éxito/error
from core.utils import enviar_email_automatico # <-- 1. Importamos tu función

def reservation_view(request):
    
    # Si el usuario envía el formulario (método POST)
    if request.method == 'POST':
        try:
            # 2. Obtenemos todos los datos del formulario
            data = {
                'nombre': request.POST.get('nombre'),
                'email': request.POST.get('email'),
                'fecha': request.POST.get('fecha'),
                'hora': request.POST.get('hora'),
                'personas': request.POST.get('personas'),
            }

            # 3. Preparamos el contexto para la plantilla de email
            context_email = {
                'nombre_cliente': data['nombre'],
                'fecha': data['fecha'],
                'hora': data['hora'],
                'personas': data['personas'],
            }

            # 4. ¡Llamamos a tu función de envío de correo!
            enviar_email_automatico(
                template_path='emails/confirmacion.html',
                context_datos=context_email,
                asunto='¡Confirmación de Reserva en The Steakhouse!',
                email_destino=data['email'] # El email que el cliente escribió
            )
            
            # (Aquí iría la lógica para guardar en la Base de Datos)
            
            # 5. Enviamos un mensaje de éxito
            messages.success(request, '¡Reserva exitosa! Hemos enviado una confirmación a tu correo.')

        except Exception as e:
            # Si algo falla (ej. el correo no se envía)
            print(f"Error en la reserva: {e}")
            messages.error(request, 'Error al procesar la reserva. Inténtalo de nuevo.')
        
        # 6. Redirigimos al usuario a la página de inicio
        return redirect('home')

    # Si el usuario solo está cargando la página (método GET)
    else:
        # Solo mostramos el formulario
        return render(request, 'reservas.html', {})