from django.urls import path
from . import views

urlpatterns = [
    # Menú principal
    path('', views.menu_view, name='menu_page'),
    
    # Acciones del carrito
    path('agregar/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('mi-pedido/', views.ver_carrito, name='ver_carrito'),

    path('confirmar/', views.confirmar_pedido, name='confirmar_pedido'),
    path('exito/<int:pedido_id>/', views.pedido_exitoso, name='pedido_exitoso'),
]