from django.urls import path
from . import views

urlpatterns = [
    path('admin/usuarios/', views.usuarios_admin, name='usuarios_admin'),
    path('admin/usuarios/<int:pk>/', views.editar_usuario_admin, name='editar_usuario_admin'),
    path('test/', views.test_endpoint, name='test_endpoint'),
]
