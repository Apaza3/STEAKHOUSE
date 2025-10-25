from django.http import HttpResponse

# Esta es tu vista de "Hola Mundo"
def home(request):
    return HttpResponse("<h1>¡Hola Mundo! Esta es la página de inicio.</h1>")