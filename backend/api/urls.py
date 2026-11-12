from django.urls import path
from . import views
from . import auth_views

urlpatterns = [
    path('admin/usuarios/', views.usuarios_admin, name='usuarios_admin'),
    path('admin/usuarios/<int:pk>/', views.editar_usuario_admin, name='editar_usuario_admin'),
    path('admin/usuarios/<int:pk>/suspender/', views.suspender_usuario_admin, name='suspender_usuario_admin'),
    path('admin/usuarios/<int:pk>/activar/', views.activar_usuario_admin, name='activar_usuario_admin'),
    path('test/', views.test_endpoint, name='test_endpoint'),
    path('db-status/', views.db_status_endpoint, name='db_status_endpoint'),
    path('health/', views.db_status_endpoint, name='health_endpoint'),
    path('registro/', auth_views.registro, name='registro'),
    path('login/', auth_views.login, name='login'),
    #nuevas rutas
    path('users/', views.list_users, name='list_users'),
    path('users/<int:user_id>/', views.update_user, name='update_user'),
    path('logout/', auth_views.logout, name='logout'),

]
