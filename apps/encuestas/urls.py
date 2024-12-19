# encuestas/urls.py
from django.urls import path
from . import views 
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

app_name = 'encuestas'

urlpatterns = [
    path('crear/', views.crear_encuesta, name='crear_encuesta'),
    path('completar/<str:codigo>/', views.completar_encuesta, name='completar_encuesta'),
    path('ver/', views.ver_encuestas, name='ver_encuestas'),
    path('ingresar-codigo/', views.ingresar_codigo, name='ingresar_codigo'),
    path('administrar/empleados/', views.administrar_empleados, name='administrar_empleados'),
    path('administrar/empleados/<int:empleado_id>/toggle/', views.toggle_empleado, name='toggle_empleado'),
    path('reportes/', views.reportes, name='reportes'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
