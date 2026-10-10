from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def test_endpoint(request):
    #Endpoint de prueba para validar la conexión con frontend.
    data = {
    "status": "success",
    "message": "Conexion existosa con el backend",
    "version": "1.0"
    }
    return Response(data)
