from django.urls import path
from . import views

urlpatterns = [
    # Esta línea usa la 'inicio_view' que arreglamos en core/views.py
    path('', views.inicio_view, name='home'),
]