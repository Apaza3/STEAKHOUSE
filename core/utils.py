from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

def enviar_email_automatico(template_path, context_datos, asunto, email_destino):
    """
    Una función reutilizable para enviar correos con plantillas HTML.
    """
    try:
        # 1. Renderiza la plantilla HTML a un string
        html_message = render_to_string(template_path, context_datos)
        
        # 2. Envía el correo
        send_mail(
            subject=asunto,
            message='',  # El mensaje de texto plano (opcional)
            from_email=settings.EMAIL_HOST_USER, # El correo configurado en settings.py
            recipient_list=[email_destino],      # La lista de destinatarios
            html_message=html_message,           # El mensaje en HTML
            fail_silently=False,
        )
        print(f"Correo enviado exitosamente a {email_destino}")
        return True
        
    except Exception as e:
        # En un proyecto real, aquí registraríamos el error
        print(f"Error al enviar correo a {email_destino}: {e}")
        return False