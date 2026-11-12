from django.contrib.auth import get_user_model
from rest_framework import serializers


class UsuarioSerializer(serializers.ModelSerializer):
    rol = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'rol', 'is_active']
        read_only_fields = ['id', 'username', 'rol', 'is_active']
        extra_kwargs = {
            'first_name': {'required': True, 'allow_blank': False},
            'last_name': {'required': True, 'allow_blank': False},
            'email': {'required': True, 'allow_blank': False},
        }

    def get_rol(self, usuario):
        return 'admin' if usuario.is_staff or usuario.is_superuser else 'cliente'

    def validate_email(self, value):
        usuarios = get_user_model().objects.filter(email__iexact=value)
        if self.instance:
            usuarios = usuarios.exclude(pk=self.instance.pk)
        if usuarios.exists():
            raise serializers.ValidationError('Este correo ya está registrado.')
        return value
