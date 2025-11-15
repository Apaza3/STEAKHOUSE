from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
import threading # <-- ¡NUEVO!

# ===================================================
# ¡NUEVO! CLASE PARA ENVIAR EMAIL EN SEGUNDO PLANO
# Esto evita que el sitio se cuelgue (Worker Timeout)
# ===================================================
class EmailThread(threading.Thread):
    def __init__(self, subject, html_message, text_message, recipient_list):
        self.subject = subject
        self.html_message = html_message
        self.text_message = text_message
        self.recipient_list = recipient_list
        threading.Thread.__init__(self)

    def run(self):
        try:
            send_mail(
                self.subject,
                self.text_message,
                settings.DEFAULT_FROM_EMAIL,
                self.recipient_list,
                html_message=self.html_message,
                fail_silently=False # Queremos que falle para que el 'except' lo atrape
            )
            print(f"Email enviado exitosamente a {self.recipient_list}")
        except Exception as e:
            # Imprime el error real en la consola de Render (ej. 535 Password, etc.)
            print(f"Error al enviar correo a {self.recipient_list}: {e}")

# ===================================================
# FUNCIÓN DE ENVÍO DE EMAIL (AHORA USA EL THREAD)
# ===================================================
def enviar_email_automatico(template_path, context_datos, asunto, email_destino):
    
    # Renderiza el template HTML a un string
    html_message = render_to_string(template_path, context_datos)
    
    # Crea un mensaje de texto plano como respaldo
    text_message = f"Hola {context_datos.get('cliente_actual', 'Cliente')}, tienes una nueva confirmación de The Steakhouse."
    
    # ¡CAMBIO! Inicia el hilo de fondo y devuelve el control a la vista
    EmailThread(
        subject=asunto,
        html_message=html_message,
        text_message=text_message,
        recipient_list=[email_destino]
    ).start()

    # La función ahora retorna inmediatamente, evitando el timeout.