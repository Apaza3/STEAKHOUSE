from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('reservas/', include('reservas.urls')),
    path('', include('core.urls')), 
    path('cuenta/', include('clientes.urls')), 
    path('pedidos/', include('pedidos.urls')),
    
    # --- ¡NUEVA LÍNEA! Conectamos el panel ---
    path('panel/', include('dashboard.urls')),
]

# (Tu configuración de static/media se queda igual)
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) # Descomenté esto, lo necesitas para las fotos de productos.