# ventas/admin.py

from django.contrib import admin
from .models import CategoriaProducto, Producto, Mesa, Pedido, DetallePedido

# --- Registros del Menú (Los que ya tenías) ---
@admin.register(CategoriaProducto)
class CategoriaProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'precio', 'disponible')
    list_filter = ('categoria', 'disponible')
    search_fields = ('nombre', 'categoria__nombre')
    list_editable = ('precio', 'disponible')

# --- NUEVOS REGISTROS Y REPORTES ---

# Registra el modelo de Mesas
admin.site.register(Mesa)


# Define cómo se ven los "Detalles" DENTRO de un Pedido
class DetallePedidoInline(admin.TabularInline):
    model = DetallePedido
    extra = 1 # Muestra 1 campo vacío para añadir
    autocomplete_fields = ['producto'] # Un buscador, mejor que un dropdown
    readonly_fields = ('precio_unitario',) # Lo calcula solo


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    """
    Esta es la configuración de tu "Almacén de Reportes"
    """
    inlines = [DetallePedidoInline] # Permite añadir productos DENTRO del pedido
    
    # Columnas que se ven en la lista de Pedidos
    list_display = ('id', 'creado_en', 'mesa', 'mesero', 'estado', 'total')
    
    # --- ¡LOS FILTROS (REPORTES)! ---
    # Esto añade una barra lateral para filtrar
    list_filter = (
        'estado',                  # Filtrar por Pagado, Pendiente, etc.
        'mesa',                    # Filtrar por Mesa
        ('creado_en', admin.DateFieldListFilter), # ¡Filtrar por Fecha!
    )
    
    # --- BÚSQUEDA ---
    search_fields = ('id', 'mesa__numero', 'mesero__username')
    
    # --- NAVEGACIÓN POR FECHA ---
    # Añade una barra de navegación por fecha en la parte superior
    date_hierarchy = 'creado_en'
    
    readonly_fields = ('total',) # El total no se edita a mano

    def save_model(self, request, obj, form, change):
        # (Lógica opcional para auto-asignar el mesero)
        if not obj.mesero:
            obj.mesero = request.user
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        # (Lógica para recalcular el total)
        instances = formset.save(commit=False)
        total_pedido = 0
        for instance in instances:
            instance.save()
            total_pedido += instance.get_subtotal()
        
        # Actualiza el total del pedido principal
        formset.instance.total = total_pedido
        formset.instance.save()
        super().save_formset(request, form, formset, change)
        