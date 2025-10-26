# ESTE ES EL CÓDIGO NUEVO (CORRECTO)
from django.shortcuts import render

def home(request):
    # Esta línea le dice a Django que use tu nueva plantilla
    return render(request, 'inicio.html', {})