# ...existing code...
from django.contrib import admin
from django.urls import path, include
from django.conf import settings # <-- NUEVO
from django.conf.urls.static import static # <-- NUEVO

urlpatterns = [
    path('2010/', admin.site.urls),
    path('reservas/', include('reservas.urls')),
    # path('auth/', include('usuarios.urls')), # (Descomenta cuando tu compañero termine)
    path('pedidos/', include('pedidos.urls')), # <-- Registramos la nueva app
    path('ventas/', include('ventas.urls')),   # <-- Añadido para reporte_ventas
    path('', include('core.urls')),
]

# Esto permite ver las imágenes subidas mientras estamos en modo DEBUG (desarrollo)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# ...existing code...