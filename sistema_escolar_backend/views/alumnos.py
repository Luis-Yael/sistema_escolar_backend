from django.db.models import *
from django.db import transaction
from sistema_escolar_backend.serializers import UserSerializer
from sistema_escolar_backend.serializers import *
from sistema_escolar_backend.models import *
from rest_framework import permissions
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth.models import Group
from sistema_escolar_backend.views.comun import (
    CAMPOS_USUARIO, respuesta_faltantes, a_fecha, mayusculas
)

ROL = "alumno"

class AlumnosAll(generics.CreateAPIView):
    #Obtener todos los alumnos
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        alumnos = Alumnos.objects.filter(user__is_active=True).order_by("id")
        lista = AlumnoSerializer(alumnos, many=True).data
        return Response(lista, 200)

class AlumnosView(generics.CreateAPIView):
    # Permisos por método (sobrescribe el comportamiento default)
    def get_permissions(self):
        if self.request.method in ['GET', 'PUT', 'DELETE']:
            return [permissions.IsAuthenticated()]
        return []  # POST no requiere autenticación

    #Registrar nuevo usuario alumno
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        user = UserSerializer(data=request.data)
        if user.is_valid():
            error = respuesta_faltantes(request.data, CAMPOS_USUARIO)
            if error:
                return error
            first_name = request.data['first_name']
            last_name = request.data['last_name']
            email = request.data['email']
            password = request.data['password']
            try:
                fecha_nacimiento = a_fecha(request.data.get("fecha_nacimiento"))
            except ValueError as e:
                return Response({"message": str(e)}, 400)
            if User.objects.filter(Q(email=email) | Q(username=email)).exists():
                return Response({"message":"El usuario "+email+" ya está registrado"},400)
            user = User.objects.create( username = email,
                                        email = email,
                                        first_name = first_name,
                                        last_name = last_name,
                                        is_active = True)
            user.set_password(password)
            user.save()

            # El rol lo define el servidor, no el cliente
            group, created = Group.objects.get_or_create(name=ROL)
            group.user_set.add(user)

            alumno = Alumnos.objects.create(user=user,
                                            matricula= request.data.get("matricula"),
                                            curp= mayusculas(request.data.get("curp")),
                                            rfc= mayusculas(request.data.get("rfc")),
                                            fecha_nacimiento= fecha_nacimiento,
                                            edad= request.data.get("edad"),
                                            telefono= request.data.get("telefono"),
                                            ocupacion= request.data.get("ocupacion"))
            return Response({"Alumno creado con ID= ": alumno.id }, 201)
        return Response(user.errors, status=status.HTTP_400_BAD_REQUEST)
