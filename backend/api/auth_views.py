from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token

@api_view(['POST'])
def registro(request):
    email = request.data.get('email')
    password = request.data.get('password')
    nombre = request.data.get('nombre', '')
    apellido = request.data.get('apellido', '')

    if not email or not password:
        return Response({'error': 'Faltan datos obligatorios (correo y contraseña).'}, status=status.HTTP_400_BAD_REQUEST)

    #Validar que el correo sea UNICO
    if User.objects.filter(username=email).exists():
        return Response({'error': 'Este correo ya se encuentra registrado.'}, status=status.HTTP_400_BAD_REQUEST)

    
    
    #Create_user se encarga de encriptar la clave de forma segura
    user = User.objects.create_user(
        username=email,
        email=email, 
        password=password,
        first_name=nombre,
        last_name=apellido
        )

    #Generamos el token para el usuario recién creado
    token, created = Token.objects.get_or_create(user=user)

    return Response({'token': token.key}, status=status.HTTP_201_CREATED)

@api_view(['POST'])
def login(request):
    email = request.data.get('email')
    password = request.data.get('password')

    try:
        user_obj = User.objects.get(username=email)
    
    except User.DoesNotExist:
        #Damos un error por si el usuario no existe
        return Response ({'error': 'Datos incorrectos.'}, status=status.HTTP_401_UNAUTHORIZED)

    #Validar si el usuario está suspendido
    if not user_obj.is_active:
        return Response({'error': 'Esta cuenta se encuentra suspendida.'}, status=status.HTTP_403_FORBIDDEN)

    #Validar que si existe y no está suspendido, la clave sea correcta
    user = authenticate(username=email, password=password)

    if user is None:
        return Response({'error': 'Datos incorrectos.'}, status=status.HTTP_401_UNAUTHORIZED)

    
    #Si todo es correcto, recuperamos su token de acceso
    token, created = Token.objects.get_or_create(user=user)
    return Response({'token': token.key}, status=status.HTTP_200_OK)
