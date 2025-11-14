from django.urls import path
from . import views

urlpatterns = [
    path('registro/', views.register_view, name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('perfil/', views.perfil_view, name='perfil'),
    
    # ===================================================
    # ¡NUEVO! RUTA PARA CAMBIAR CONTRASEÑA
    # ===================================================
    path('password/', views.CustomPasswordChangeView.as_view(), name='password_change'),
]