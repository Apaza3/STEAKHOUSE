from django.urls import path
from . import views

urlpatterns = [
    path('registro/', views.register_view, name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('perfil/', views.perfil_view, name='perfil'),
    path('password/', views.CustomPasswordChangeView.as_view(), name='password_change'),
    
    # ===================================================
    # ¡NUEVO! RUTAS PARA GESTIONAR "MIS RESERVAS"
    # ===================================================
    path('mis-reservas/', views.mis_reservas_view, name='mis_reservas'),
    path('cancelar-reserva/<uuid:reserva_id>/', views.cancelar_reserva_view, name='cancelar_reserva'),
]