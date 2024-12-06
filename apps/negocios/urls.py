from django.urls import path
from . import views

urlpatterns = [
    path('registro/', views.registro_negocio, name='registro_negocio'),
    path('login/', views.login_negocio, name='login_negocio'),
    path('dashboard/', views.dashboard, name='dashboard'),
]