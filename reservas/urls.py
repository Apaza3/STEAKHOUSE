from django.urls import path
from . import views

urlpatterns = [
    # /reservas/
    path('', views.reservation_view, name='reservas_page'),
    
    # /reservas/espera-qr/UUID/
    path('espera-qr/<uuid:reserva_id>/', views.payment_waiting_view, name='payment_waiting_view'),
    
    # /reservas/confirmar-qr/UUID/  (Para el celular)
    path('confirmar-qr/<uuid:reserva_id>/', views.payment_confirm_view, name='payment_confirm_view'),
    
    # /reservas/estado-reserva/UUID/ (Para el polling)
    path('estado-reserva/<uuid:reserva_id>/', views.check_reservation_status_view, name='check_reservation_status_view'),
    
    # /reservas/pago-tarjeta/UUID/
    path('pago-tarjeta/<uuid:reserva_id>/', views.payment_tarjeta_view, name='payment_tarjeta_view'),

    # /reservas/confirmar-tarjeta/UUID/
    path('confirmar-tarjeta/<uuid:reserva_id>/', views.payment_tarjeta_confirm, name='payment_tarjeta_confirm'),
]