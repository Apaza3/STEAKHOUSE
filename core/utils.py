from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
import threading

# ===================================================
# CLASE PARA ENVIAR EMAIL EN SEGUNDO PLANO (CORREGIDA)
# ===================================================
class EmailThread(threading.Thread):
    def __init__(self, subject, html_message, text_message, recipient_list):
        self.subject = subject
        self.html_message = html_message
        self.text_message = text_message
        self.recipient_list = recipient_list
        
        # ¡¡¡ESTE ES EL CAMBIO CRÍTICO!!!
        # Usamos super().__init__() en lugar de threading.Thread.__init__(self)
        # Esto asegura que el método run() sea llamado por start()
        super().__init__() 

    def run(self):
        # Ahora, este código SÍ se ejecutará
        try:
            print(f"Intentando enviar email a {self.recipient_list} vía Brevo...")
            send_mail(
                self.subject,
                self.text_message,
                settings.DEFAULT_FROM_EMAIL,
                self.recipient_list,
                html_message=self.html_message,
                fail_silently=False 
            )
            print(f"Email enviado exitosamente a {self.recipient_list}")
        except Exception as e:
            # Ahora SÍ veremos el error real en los logs de Render
            print(f"Error al enviar correo a {self.recipient_list}: {e}")

# ===================================================
# FUNCIÓN DE ENVÍO (Sin cambios)
# ===================================================
def enviar_email_automatico(template_path, context_datos, asunto, email_destino):
    
    html_message = render_to_string(template_path, context_datos)
    
    text_message = f"Hola {context_datos.get('cliente_actual', 'Cliente')}, tienes una nueva confirmación de The Steakhouse."
    
    EmailThread(
        subject=asunto,
        html_message=html_message,
        text_message=text_message,
        recipient_list=[email_destino]
    ).start()
