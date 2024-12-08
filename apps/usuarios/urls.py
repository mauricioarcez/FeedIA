from django.urls import path
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from . import views

app_name = 'apps.usuarios'  # Namespace para tus URLs

urlpatterns = [
    path('registro/', views.RegistroUsuarioView.as_view(), name='registro_usuario'),
    path('login/', auth_views.LoginView.as_view(template_name="usuarios/iniciar_sesion.html"), name='usuario_login'),  # Vista de login
    path('logout/', auth_views.LogoutView.as_view(), name='usuario_logout'),  # Vista de logout
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)