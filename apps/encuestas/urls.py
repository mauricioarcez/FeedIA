from django.urls import path
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from . import views 

urlpatterns = [
    path('generar_encuesta/<str:negocio>/', views.generar_encuesta, name='generar_encuesta'),
    path('validar_encuesta/', views.validar_encuesta, name='validar_encuesta'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)