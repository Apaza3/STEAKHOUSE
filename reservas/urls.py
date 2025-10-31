from django.urls import path
from . import views

urlpatterns = [
    # Cuando alguien visite '.../reservas/', se llamará a esta vista
    path('', views.reservation_view, name='reservas_page'),
]