from django.db import models
from django.contrib.auth.models import User

# ==============================================================================
# TAREA 2 BACKEND: MODELOS RELACIONALES (PostgreSQL)
# Justificación: Datos transaccionales que requieren integridad referencial,
# cumplimiento ACID, claves foráneas y consistencia estricta en ventas e inventario.
# ==============================================================================

class Categoria(models.Model):
    """
    Categoría para clasificar productos (ej: Cafés de Especialidad, Grano, Molido, Repostería, Accesorios)
    """
    nombre = models.CharField(max_length=100, unique=True, verbose_name="nombre de la categoria")
    slug = models.SlugField(max_length=120, unique=True, verbose_name="slug amigable para url")
    descripcion = models.TextField(blank=True, verbose_name="descripcion")
    activo = models.BooleanField(default=True, verbose_name="activo en el catalogo")
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "categoria"
        verbose_name_plural = "categorias"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    """
    Catálogo de productos de la cafetería con control de precio y stock comercial.
    """
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.CASCADE,
        related_name="productos",
        verbose_name="categoria"
    )
    nombre = models.CharField(max_length=150, verbose_name="nombre del producto")
    slug = models.SlugField(max_length=180, unique=True, verbose_name="slug url")
    descripcion = models.TextField(verbose_name="descripcion comercial")
    precio = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="precio (clp)")
    stock = models.PositiveIntegerField(default=0, verbose_name="unidades en inventario")
    disponible = models.BooleanField(default=True, verbose_name="disponible para la venta")
    imagen_url = models.URLField(max_length=500, blank=True, verbose_name="url de la imagen")
    formato = models.CharField(max_length=50, blank=True, help_text="ej: '250g', '500g', '1kg', 'porcion'", verbose_name="formato/presentacion")
    destacado = models.BooleanField(default=False, verbose_name="mostrar en destacados / hero")
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "producto"
        verbose_name_plural = "productos"
        ordering = ['-destacado', 'nombre']

    def __str__(self):
        return f"{self.nombre} (${self.precio})"


class Pedido(models.Model):
    """
    Orden de compra generada por un cliente en el flujo de carrito y pago.
    """
    ESTADOS = [
        ('PENDIENTE', 'pendiente de pago'),
        ('PAGADO', 'pagado con exito'),
        ('PREPARANDO', 'en preparacion'),
        ('LISTO', 'listo para retiro / despacho'),
        ('ENTREGADO', 'entregado al cliente'),
        ('CANCELADO', 'cancelado / anulado'),
    ]

    TIPOS_ENTREGA = [
        ('retiro', 'retiro en cafeteria'),
        ('despacho', 'despacho a domicilio'),
    ]

    usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="pedidos",
        verbose_name="usuario registrado"
    )
    cliente_nombre = models.CharField(max_length=150, verbose_name="nombre completo del cliente")
    cliente_email = models.EmailField(verbose_name="correo electronico")
    cliente_telefono = models.CharField(max_length=20, blank=True, verbose_name="telefono de contacto")
    tipo_entrega = models.CharField(max_length=20, choices=TIPOS_ENTREGA, default='retiro', verbose_name="metodo de entrega")
    direccion_entrega = models.CharField(max_length=255, blank=True, verbose_name="direccion de despacho")
    notas = models.TextField(blank=True, verbose_name="instrucciones o notas adicionales")

    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="subtotal")
    costo_envio = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="costo de envio")
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="monto total")

    estado = models.CharField(max_length=20, choices=ESTADOS, default='PENDIENTE', verbose_name="estado del pedido")
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "pedido"
        verbose_name_plural = "pedidos"
        ordering = ['-creado_en']

    def __str__(self):
        return f"pedido #{self.id} - {self.cliente_nombre} (${self.total}) [{self.estado}]"


class DetallePedido(models.Model):
    """
    Ítems individuales dentro de una orden de compra.
    """
    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name="detalles",
        verbose_name="pedido asociado"
    )
    producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,
        verbose_name="producto"
    )
    cantidad = models.PositiveIntegerField(default=1, verbose_name="cantidad")
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="precio unitario al comprar")
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="subtotal del item")

    class Meta:
        verbose_name = "detalle del pedido"
        verbose_name_plural = "detalles del pedido"

    def __str__(self):
        return f"{self.cantidad}x {self.producto.nombre} en pedido #{self.pedido_id}"


class PagoTransaccion(models.Model):
    """
    Registro contable y formal de la transacción en la pasarela externa de pago.
    """
    ESTADOS_PAGO = [
        ('INICIADO', 'iniciado'),
        ('AUTORIZADO', 'aprobado / autorizado'),
        ('RECHAZADO', 'rechazado'),
        ('REVERSADO', 'reversado / reembolsado'),
    ]

    pedido = models.OneToOneField(
        Pedido,
        on_delete=models.CASCADE,
        related_name="pago",
        verbose_name="pedido"
    )
    pasarela = models.CharField(
        max_length=50,
        default='webpay plus',
        help_text="nombre del proveedor externo (ej: webpay plus, stripe, mercadopago)"
    )
    token_pasarela = models.CharField(max_length=255, unique=True, null=True, blank=True, verbose_name="token de sesion o pago")
    transaccion_id_externo = models.CharField(max_length=150, blank=True, verbose_name="id de transaccion del banco/pasarela")
    monto = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="monto cobrado")
    estado = models.CharField(max_length=20, choices=ESTADOS_PAGO, default='INICIADO', verbose_name="estado de transaccion")
    codigo_autorizacion = models.CharField(max_length=50, blank=True, verbose_name="codigo de autorizacion bancaria")
    fecha_transaccion = models.DateTimeField(auto_now_add=True)
    fecha_confirmacion = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "transaccion de pago"
        verbose_name_plural = "transacciones de pagos"

    def __str__(self):
        return f"pago {self.pasarela} - pedido #{self.pedido_id} - estado: {self.estado}"


# ==============================================================================
# SPRINT 4 BACKEND: TEMA VISUAL ACTIVO Y MENSAJES DE CONTACTO (PostgreSQL)
# Justificación (spec): "PostgreSQL: usuarios, tema visual activo, mensajes de
# contacto". Son datos estructurados con validación estricta y baja variabilidad.
# ==============================================================================

class TemaVisual(models.Model):
    """
    Los cuatro temas visuales aprobados (Claro, Oscuro, Vintage, Pastel).
    Exactamente un tema queda con activo=True: es el tema activo del sitio,
    persistido en la base de datos (sobrevive reinicios, HU-06 / RF-04).
    """
    NOMBRES_APROBADOS = ['claro', 'oscuro', 'vintage', 'pastel']

    nombre = models.SlugField(max_length=20, unique=True, verbose_name="identificador del tema")
    etiqueta = models.CharField(max_length=40, verbose_name="nombre visible")
    activo = models.BooleanField(default=False, verbose_name="tema activo del sitio")
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "tema visual"
        verbose_name_plural = "temas visuales"
        ordering = ['nombre']

    def __str__(self):
        return f"{self.etiqueta} ({'activo' if self.activo else 'inactivo'})"

    @classmethod
    def garantizar_temas(cls):
        """Crea los cuatro temas aprobados si no existen y devuelve el activo
        (o el tema 'claro' por defecto)."""
        for nombre in cls.NOMBRES_APROBADOS:
            cls.objects.get_or_create(
                nombre=nombre,
                defaults={'etiqueta': nombre.capitalize(), 'activo': nombre == 'claro'}
            )
        activo = cls.objects.filter(activo=True).first()
        if activo is None:
            activo = cls.objects.filter(nombre='claro').first()
            if activo is None:
                activo = cls.objects.create(nombre='claro', etiqueta='Claro', activo=True)
            else:
                activo.activo = True
                activo.save(update_fields=['activo', 'actualizado_en'])
        return activo


class MensajeContacto(models.Model):
    """
    Mensaje enviado desde el formulario público de contacto (HU-07 / RF-05).
    Validaciones de negocio: nombre 2-100 caracteres, correo con formato válido
    y mensaje de 10 a 2.000 caracteres (validadas en el endpoint).
    """
    nombre = models.CharField(max_length=100, verbose_name="nombre del remitente")
    email = models.EmailField(verbose_name="correo de contacto")
    mensaje = models.TextField(verbose_name="mensaje")
    leido = models.BooleanField(default=False, verbose_name="leido por administracion")
    creado_en = models.DateTimeField(auto_now_add=True, verbose_name="fecha de recepcion")

    class Meta:
        verbose_name = "mensaje de contacto"
        verbose_name_plural = "mensajes de contacto"
        ordering = ['-creado_en']

    def __str__(self):
        return f"{self.nombre} <{self.email}> - {self.creado_en:%Y-%m-%d}"
