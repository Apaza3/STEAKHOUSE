from django.urls import path
from . import views

urlpatterns = [
    path('', views.reservation_view, name='reservas_page'),
    
    # ... tus otras rutas de pago ...
    path('pago/espera/<uuid:reserva_id>/', views.payment_waiting_view, name='payment_waiting_view'),
    path('pago/confirmar/<uuid:reserva_id>/', views.payment_confirm_view, name='payment_confirm_view'),
    path('pago/tarjeta/<uuid:reserva_id>/', views.payment_tarjeta_view, name='payment_tarjeta_view'),
    path('pago/tarjeta/confirmar/<uuid:reserva_id>/', views.payment_tarjeta_confirm, name='payment_tarjeta_confirm'),
    path('api/status/<uuid:reserva_id>/', views.check_reservation_status_view, name='check_reservation_status_view'),

    # --- ¡NUEVA RUTA API! ---
    path('api/check-mesas/', views.api_mesas_disponibles, name='api_check_mesas'),
]