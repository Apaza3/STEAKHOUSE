from django.urls import path
from . import views

urlpatterns = [
    # /pedidos/menu/
    path('menu/', views.menu_view, name='menu_page'),
    
    # /pedidos/carrito/
    path('carrito/', views.ver_carrito_view, name='ver_carrito'),
    
    # /pedidos/agregar/1/
    path('agregar/<int:producto_id>/', views.agregar_al_carrito_view, name='agregar_al_carrito'),
    
    # /pedidos/confirmar/
    path('confirmar/', views.confirmar_pedido_view, name='confirmar_pedido'),
    
    # /pedidos/exitoso/
    path('exitoso/', views.pedido_exitoso_view, name='pedido_exitoso'),
    
    # --- ¡NUEVA URL! ---
    # /pedidos/mis-pedidos/
    path('mis-pedidos/', views.mis_pedidos_view, name='mis_pedidos'),
]