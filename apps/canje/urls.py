from django.urls import path
from . import views 
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

app_name = 'canje'

urlpatterns = [
        path('administrar/canjes/', views.administrar_canjear, name='administrar_canjear'), 
        path('administrar/canjear/', views.canjear_puntos, name='canjear'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)