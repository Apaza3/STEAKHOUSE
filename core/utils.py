# core/utils.py

from __future__ import absolute_import
import threading
from django.template.loader import render_to_string
from django.conf import settings # Para leer la API Key y el email

# ¡NUEVAS IMPORTACIONES! (Requiere 'pip install sib-api-v3-sdk')
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

# ===================================================
# CLASE PARA ENVIAR EMAIL (AHORA USA LA API DE BREVO)
# ===================================================
class EmailThread(threading.Thread):
    def __init__(self, subject, html_message, sender_email, recipient_email):
        self.subject = subject
        self.html_message = html_message
        self.sender_email = sender_email
        self.recipient_email = recipient_email
        super().__init__() 

    def run(self):
        # 1. Configurar la API de Brevo
        configuration = sib_api_v3_sdk.Configuration()
        # Leemos la API key desde settings.py, que la lee de os.environ
        configuration.api_key['api-key'] = settings.BREVO_API_KEY
        
        api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
        
        # 2. Preparar el email
        # El email de envío debe estar VERIFICADO en Brevo
        sender = sib_api_v3_sdk.SendSmtpEmailSender(email=self.sender_email, name="The Steakhouse")
        to = [sib_api_v3_sdk.SendSmtpEmailTo(email=self.recipient_email)]
        
        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
            to=to,
            sender=sender,
            subject=self.subject,
            html_content=self.html_message
        )

        # 3. Enviar el email (por HTTPS, no SMTP)
        try:
            print(f"Intentando enviar email a {self.recipient_email} vía API de Brevo...")
            api_response = api_instance.send_transac_email(send_smtp_email)
            print(f"Email enviado exitosamente a {self.recipient_email}. Response: {api_response}")
        except ApiException as e:
            # Ahora veremos el error real de la API (ej. 'Invalid API Key', 'Sender not verified')
            print(f"Error de API de Brevo al enviar a {self.recipient_email}: {e}")
        except Exception as e:
            print(f"Error general en EmailThread: {e}")

# ===================================================
# FUNCIÓN DE ENVÍO (Modificada para la API)
# ===================================================
def enviar_email_automatico(template_path, context_datos, asunto, email_destino):
    
    html_message = render_to_string(template_path, context_datos)
    
    # ¡IMPORTANTE! Leemos el email de envío desde settings.py
    sender_email = settings.DEFAULT_SENDER_EMAIL
    if not sender_email:
        print("ERROR: DEFAULT_SENDER_EMAIL no está configurado en Render.")
        return
    if not settings.BREVO_API_KEY:
        print("ERROR: BREVO_API_KEY no está configurado en Render.")
        return

    EmailThread(
        subject=asunto,
        html_message=html_message,
        sender_email=sender_email, # Email verificado en Brevo
        recipient_email=email_destino
    ).start()