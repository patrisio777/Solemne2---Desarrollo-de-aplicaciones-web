from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.decorators import permission_classes
from django.contrib.auth import get_user_model
from django.middleware.csrf import get_token
from django.shortcuts import get_object_or_404
from .serializers import UsuarioSerializer
from .permissions import EsAdministrador

@api_view(['GET'])
def test_endpoint(request):
    #Endpoint de prueba para validar la conexión con frontend.
    data = {
    "status": "success",
    "message": "Conexion existosa con el backend",
    "version": "1.0"
    }
    return Response(data)


@api_view(['GET'])
@permission_classes([EsAdministrador])
def usuarios_admin(request):
    usuarios = get_user_model().objects.order_by('first_name', 'last_name', 'pk')
    return Response({
        'usuario_actual_id': request.user.pk,
        'csrf_token': get_token(request),
        'usuarios': UsuarioSerializer(usuarios, many=True).data,
    })


@api_view(['PATCH'])
@permission_classes([EsAdministrador])
def editar_usuario_admin(request, pk):
    if pk == request.user.pk:
        return Response({'detail': 'No puedes editar tu propia cuenta desde este panel.'}, status=403)
    usuario = get_object_or_404(get_user_model(), pk=pk)
    permitidos = {'first_name', 'last_name', 'email'}
    if not request.data or set(request.data) - permitidos:
        return Response({'detail': 'Solo puedes modificar nombre, apellido y correo.'}, status=400)
    serializer = UsuarioSerializer(usuario, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)
