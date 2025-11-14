from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_home, name='dashboard_home'),
    
    # URLs de Productos
    path('productos/', views.producto_list, name='dashboard_productos'),
    path('productos/crear/', views.producto_create, name='producto_create'),
    path('productos/editar/<int:pk>/', views.producto_update, name='producto_update'),
    path('productos/eliminar/<int:pk>/', views.producto_delete, name='producto_delete'),
    
    # ===============================================
    # ¡NUEVO! URLs DE MESAS (CRUD)
    # ===============================================
    path('mesas/', views.mesa_list, name='dashboard_mesas'),
    path('mesas/crear/', views.mesa_create, name='mesa_create'),
    path('mesas/editar/<int:pk>/', views.mesa_update, name='mesa_update'),
    path('mesas/eliminar/<int:pk>/', views.mesa_delete, name='mesa_delete'),
    # ===============================================

    # URLs DE USUARIOS (¡CORREGIDAS!)
    path('empleados/', views.empleado_list, name='dashboard_empleados'),
    path('clientes/', views.cliente_list, name='dashboard_clientes'),
    path('usuarios/toggle-staff/<int:user_id>/', views.user_toggle_staff, name='user_toggle_staff'),
    path('usuarios/eliminar/<int:user_id>/', views.user_delete, name='user_delete'),
    
    # URLs de Reportes
    path('reportes/', views.reportes_ventas_view, name='dashboard_reportes'),
    
    # URLs de Pedidos
    path('pedidos/', views.pedido_list, name='dashboard_pedidos'),
    path('pedidos/detalle/<int:pk>/', views.pedido_detail, name='pedido_detail'),
]