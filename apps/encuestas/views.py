import qrcode
from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseForbidden
from .models import Encuesta


def generar_encuesta(request, negocio):
    """Genera una nueva encuesta con código único y QR."""
    """#+
    Generates a new survey with a unique code and QR code.#+
#+
    This function creates a new survey entry in the database, generates a unique URL#+
    for the survey, and creates a QR code image for easy access to the survey.#+
#+
    Parameters:#+
    request (HttpRequest): The HTTP request object (not used in the function, but required by Django).#+
    negocio (str): The name or identifier of the business for which the survey is being created.#+
#+
    Returns:#+
    HttpResponse: A response containing a message with the created survey code and the filename of the generated QR code.#+
    """
    encuesta = Encuesta.objects.create(negocio=negocio)
    url = url = f"http://127.0.0.1:8000/validar_encuesta/?codigo={encuesta.codigo}"

    # Generar QR
    qr = qrcode.make(url)
    qr_filename = f"qr_{encuesta.codigo}.png"
    qr.save(f"media/{qr_filename}")

    return HttpResponse(f"Encuesta creada: {encuesta.codigo}. QR generado en: {qr_filename}")


def validar_encuesta(request):
    """
    Validates the survey code and allows access if it's valid.

    This function checks if the provided survey code is valid and unused. If the code
    is valid, it marks the survey as used and renders the survey form. If the code
    is invalid or already used, it returns a forbidden response.

    Parameters:
    request (HttpRequest): The HTTP request object containing the GET parameters.

    Returns:
    HttpResponse: If the code is valid, renders the 'encuesta_form.html' template.
    HttpResponseForbidden: If the code is invalid or already used, returns a forbidden response.
    """
    codigo = request.GET.get("codigo")
    encuesta = Encuesta.objects.filter(codigo=codigo, usada=False).first()

    if not encuesta:
        return HttpResponseForbidden("Código inválido o ya utilizado.")

    # Marcar la encuesta como usada
    encuesta.usada = True
    encuesta.save()

    return render(request, "encuesta_form.html")
