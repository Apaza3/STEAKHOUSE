from django.shortcuts import render

# Create your views here.

def inicio_view(request):
    """
    Vista simple que solo renderiza la plantilla de la página de inicio.
    """
    return render(request, 'inicio.html')