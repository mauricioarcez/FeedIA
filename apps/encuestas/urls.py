from django.urls import path
from . import views  # Asegúrate de que la vista esté importada

urlpatterns = [
    # Aquí puedes agregar las rutas específicas para la app encuestas
    path('', views.home, name='home'),  # Esto es solo un ejemplo, si tienes una vista home
]