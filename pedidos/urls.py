from django.urls import path
from . import views

urlpatterns = [
    # /pedidos/menu/
    path('menu/', views.menu_view, name='menu_page'),
    
    # /pedidos/carrito/ (Redirige al menú por ahora, el carrito es un modal)
    path('carrito/', views.ver_carrito_view, name='ver_carrito'),
    
    # /pedidos/agregar/1/
    path('agregar/<int:producto_id>/', views.agregar_al_carrito_view, name='agregar_al_carrito'),

    # --- ¡NUEVA RUTA! Eliminar del carrito ---
    # /pedidos/eliminar/1/
    path('eliminar/<int:producto_id>/', views.eliminar_del_carrito_view, name='eliminar_del_carrito'),
    
    # /pedidos/confirmar/
    path('confirmar/', views.confirmar_pedido_view, name='confirmar_pedido'),
    
    # /pedidos/exitoso/
    path('exitoso/', views.pedido_exitoso_view, name='pedido_exitoso'),
    
    # /pedidos/mis-pedidos/
    path('mis-pedidos/', views.mis_pedidos_view, name='mis_pedidos'),
]