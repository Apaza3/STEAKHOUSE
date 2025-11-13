from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('reservas/', include('reservas.urls')),
    path('', include('core.urls')), 
    path('cuenta/', include('clientes.urls')), 
    
    # --- ¡ARREGLO! AÑADIR ESTA LÍNEA ---
    path('pedidos/', include('pedidos.urls')),
    # ------------------------------------
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    # urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)