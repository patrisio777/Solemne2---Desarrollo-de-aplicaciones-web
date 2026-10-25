from django.contrib import admin
from .models import Categoria, Producto, Pedido, DetallePedido, PagoTransaccion

class DetallePedidoInline(admin.TabularInline):
    model = DetallePedido
    extra = 0
    readonly_fields = ('subtotal',)

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'slug', 'activo', 'creado_en')
    prepopulated_fields = {'slug': ('nombre',)}
    search_fields = ('nombre',)
    list_filter = ('activo',)

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'precio', 'stock', 'disponible', 'destacado')
    list_filter = ('categoria', 'disponible', 'destacado')
    search_fields = ('nombre', 'descripcion')
    prepopulated_fields = {'slug': ('nombre',)}
    list_editable = ('precio', 'stock', 'disponible', 'destacado')

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente_nombre', 'cliente_email', 'total', 'estado', 'tipo_entrega', 'creado_en')
    list_filter = ('estado', 'tipo_entrega', 'creado_en')
    search_fields = ('cliente_nombre', 'cliente_email', 'id')
    inlines = [DetallePedidoInline]

@admin.register(PagoTransaccion)
class PagoTransaccionAdmin(admin.ModelAdmin):
    list_display = ('id', 'pedido', 'pasarela', 'monto', 'estado', 'codigo_autorizacion', 'fecha_transaccion')
    list_filter = ('pasarela', 'estado')
    search_fields = ('token_pasarela', 'codigo_autorizacion', 'pedido__id')
