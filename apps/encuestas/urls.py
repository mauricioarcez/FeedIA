from django.urls import path
from . import views 

urlpatterns = [
    path('generar_encuesta/<str:negocio>/', views.generar_encuesta, name='generar_encuesta'),
    path('validar_encuesta/', views.validar_encuesta, name='validar_encuesta'),
]