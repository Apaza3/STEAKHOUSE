from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_home, name='dashboard_home'),
    
    # URLs de Productos
    path('productos/', views.producto_list, name='dashboard_productos'),
    path('productos/crear/', views.producto_create, name='producto_create'),
    path('productos/editar/<int:pk>/', views.producto_update, name='producto_update'),
    path('productos/eliminar/<int:pk>/', views.producto_delete, name='producto_delete'),
    
    # --- ¡NUEVAS LÍNEAS! ---
    # URLs de Usuarios
    path('usuarios/', views.user_list, name='dashboard_usuarios'),
    path('usuarios/toggle-staff/<int:user_id>/', views.user_toggle_staff, name='user_toggle_staff'),
    path('usuarios/eliminar/<int:user_id>/', views.user_delete, name='user_delete'),
]