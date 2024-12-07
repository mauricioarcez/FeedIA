from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from .views import RegistrarNegocioView, ReportesView, PerfilView
from django.contrib.auth.views import LoginView, LogoutView

app_name = 'apps.negocios'

urlpatterns = [
    # Registro de negocios
    path('registrar/', RegistrarNegocioView.as_view(), name='registrar_negocio'),
    
    # Login y Logout
    path('iniciar_sesion/', LoginView.as_view(template_name='negocios/iniciar_sesion.html'), name='iniciar_sesion'),
    path('cerrar_sesion/', LogoutView.as_view(), name='cerrar_sesion'),
    
    # Reportes del negocio (solo si está logueado)
    path('reportes/', ReportesView.as_view(), name='reportes'),
    
    # Agregar la ruta del perfil
    path('perfil/', PerfilView.as_view(), name='perfil_negocio'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

