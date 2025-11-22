from django.urls import path
from . import views

urlpatterns = [
    # Vista del Menú Principal
    path('menu/', views.menu_view, name='menu_page'),
    
    # Historial de Pedidos (Cliente)
    path('mis-pedidos/', views.mis_pedidos_view, name='mis_pedidos'),

    # Acciones del Carrito (AJAX)
    path('agregar/<int:producto_id>/', views.agregar_al_carrito_view, name='agregar_al_carrito'),
    path('eliminar/<int:producto_id>/', views.eliminar_del_carrito_view, name='eliminar_del_carrito'),
    
    # --- NUEVAS RUTAS PARA EL FLUJO DE MESA ---
    path('seleccionar-mesa/', views.seleccionar_mesa_view, name='seleccionar_mesa'),
    path('confirmar/', views.confirmar_pedido_view, name='confirmar_pedido'),
    
    # Página de Éxito
    path('pedido-exitoso/', views.pedido_exitoso_view, name='pedido_exitoso'),
]