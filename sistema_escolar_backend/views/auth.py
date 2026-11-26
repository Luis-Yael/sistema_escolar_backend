from django.db.models import *
from sistema_escolar_backend.serializers import *
from sistema_escolar_backend.models import *
from rest_framework import permissions
from rest_framework import generics
from rest_framework import status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

def prohibido(mensaje):
    # Respuesta 403 con el motivo del rechazo
    return Response({"details": mensaje}, status=status.HTTP_403_FORBIDDEN)

class CustomAuthToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                        context={'request': request})

        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        if not user.is_active:
            return prohibido("El usuario está inactivo")

        # Un usuario sin grupo asignado no tiene rol válido
        grupo = user.groups.first()
        if grupo is None:
            return prohibido("El usuario no tiene un rol asignado")
        role_name = grupo.name

        #Esta función genera la clave dinámica (token) para iniciar sesión
        token, created = Token.objects.get_or_create(user=user)

        if role_name == 'alumno':
            perfil = Alumnos.objects.filter(user=user).first()
            serializer_perfil = AlumnoSerializer
        elif role_name == 'maestro':
            perfil = Maestros.objects.filter(user=user).first()
            serializer_perfil = MaestroSerializer
        elif role_name == 'administrador':
            data = UserSerializer(user, many=False).data
            data['token'] = token.key
            data["rol"] = "administrador"
            return Response(data, 200)
        else:
            return prohibido("Acceso denegado: el rol no es válido")

        if perfil is None:
            return prohibido("El usuario no tiene perfil registrado")
        data = serializer_perfil(perfil).data
        data["token"] = token.key
        data["rol"] = role_name
        return Response(data, 200)


class Logout(generics.GenericAPIView):

    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        user = request.user
        if user.is_active:
            Token.objects.filter(user=user).delete()
            return Response({'logout':True})

        return Response({'logout': False})
