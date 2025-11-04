# ventas/urls.py

from django.urls import path
from . import views  # Importa las vistas de la app 'ventas'

urlpatterns = [
    # Esta será la página de tu menú
    path('menu/', views.mostrar_menu, name='menu'),
    path('reportes/', views.ver_reporte_ventas, name='reporte_ventas'),
]