from django.urls import path
from . import views

urlpatterns = [
    # --- Flujo de Reserva ---
    # Esto le dice a Django: "Cuando alguien visite /reservas/, 
    # usa la vista 'reservation_view'"
    path('', views.reservation_view, name='reservas_page'),
    
    # --- Flujo de Simulación de Pago QR ---
    
    # 1. La página que muestra el QR (para la PC)
    path('esperando-pago/<uuid:id_reserva>/', views.payment_waiting_view, name='payment_waiting'),

    # 2. La URL que va DENTRO del QR (para el Celular)
    path('confirmar-pago/<uuid:id_reserva>/', views.payment_confirm_view, name='payment_confirm'),
    
    # 3. La URL de la API que revisa el estado (para el JavaScript)
    path('api/estado-reserva/<uuid:id_reserva>/', views.check_reservation_status_view, name='check_reservation_status'),
]