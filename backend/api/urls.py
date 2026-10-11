from django.urls import path
from . import views
from . import auth_views

urlpatterns = [
    path('test/', views.test_endpoint, name='test_endpoint'),
    path('registro/', auth_views.registro, name='registro'),
    path('login/', auth_views.login, name='login'),
]