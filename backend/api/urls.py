from django.urls import path
from . import views
from . import auth_views
from . import productos_views
from . import config_views

urlpatterns = [
    path('test/', views.test_endpoint, name='test_endpoint'),
    path('db-status/', views.db_status_endpoint, name='db_status_endpoint'),
    path('health/', views.db_status_endpoint, name='health_endpoint'),
    path('registro/', auth_views.registro, name='registro'),
    path('login/', auth_views.login, name='login'),
    path('logout/', auth_views.logout, name='logout'),

    # Gestion de usuarios (HU-08) - API unificada con autorizacion por roles
    path('users/', views.list_users, name='list_users'),
    path('users/<int:user_id>/', views.update_user, name='update_user'),

    # Panel de administracion de cuentas (HU-08)
    path('admin/usuarios/', views.usuarios_admin, name='usuarios_admin'),
    path('admin/usuarios/<int:pk>/', views.editar_usuario_admin, name='editar_usuario_admin'),
    path('admin/usuarios/<int:pk>/suspender/', views.suspender_usuario_admin, name='suspender_usuario_admin'),
    path('admin/usuarios/<int:pk>/activar/', views.activar_usuario_admin, name='activar_usuario_admin'),

    # Autorizacion por roles (perfil cliente / panel administrador)
    path('perfil/', views.perfil_cliente, name='perfil_cliente'),
    path('admin-panel/', views.panel_administrador, name='panel_administracion'),

    # Catalogo de productos en MongoDB Atlas (Sprint 3/4 - HU-08 / HU-09)
    path('productos/', productos_views.catalogo_productos, name='productos_catalogo'),
    path('productos/<str:identificador>/', productos_views.detalle_o_edicion, name='producto_detalle'),
    path('productos/<str:identificador>/estado/', productos_views.cambiar_estado_producto, name='producto_estado'),
    path('productos/<str:identificador>/stock/', productos_views.ajustar_stock_producto, name='producto_stock'),

    # Tema visual activo y mensajes de contacto en PostgreSQL (Sprint 4 - HU-06 / HU-07)
    path('tema/', config_views.tema_activo, name='tema_activo'),
    path('contacto/', config_views.crear_mensaje_contacto, name='crear_mensaje_contacto'),
    path('contacto/mensajes/', config_views.listar_mensajes_contacto, name='listar_mensajes_contacto'),
]
