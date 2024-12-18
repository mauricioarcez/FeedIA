# encuestas/urls.py
from django.urls import path
from . import views 
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

app_name = 'apps.encuestas'

urlpatterns = [
    path('crear/', views.crear_encuesta, name='crear_encuesta'),
    path('completar/<str:codigo>/', views.completar_encuesta, name='completar_encuesta'),
    path('ver/', views.ver_encuestas, name='ver_encuestas'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
