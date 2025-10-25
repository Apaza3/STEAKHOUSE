from django.urls import path
from . import views  # Importa las vistas (views.py) de esta app

urlpatterns = [
    # Cuando alguien visite la URL raíz, llama a la vista "home"
    path('', views.home, name='home'),
]