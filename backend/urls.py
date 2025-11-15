from django.contrib import admin
from django.urls import path, include, re_path # ¡Importación añadida!
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve # ¡Importación añadida!

urlpatterns = [
    path('admin/', admin.site.urls),
    path('reservas/', include('reservas.urls')),
    path('', include('core.urls')), 
    path('cuenta/', include('clientes.urls')), 
    path('pedidos/', include('pedidos.urls')),
    
    # --- ¡NUEVA LÍNEA! Conectamos el panel ---
    path('panel/', include('dashboard.urls')),
]

# Tu bloque original para desarrollo (DEBUG=True)
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# ¡NUEVO!
# Añadimos esto *fuera* del if DEBUG para que Render (DEBUG=False)
# pueda encontrar los archivos media (fotos de perfil, etc.)
# Esto es esencial para que tus fotos de perfil se vean en producción.
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {
        'document_root': settings.MEDIA_ROOT,
    }),
]