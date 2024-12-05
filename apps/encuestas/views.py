from django.shortcuts import render

def home(request):
    """
    Vista para la página de inicio de las encuestas.

    Esta vista renderiza el template 'home.html' para mostrar el contenido relacionado con las encuestas.
    """
    return render(request, 'encuestas/home.html')
