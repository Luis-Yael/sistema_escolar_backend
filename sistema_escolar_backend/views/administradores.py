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
from sistema_escolar_backend.views.comun import CAMPOS_USUARIO, respuesta_faltantes, mayusculas

ROL = "administrador"

class AdminAll(generics.CreateAPIView):
    #Esta función es esencial para todo donde se requiera autorización de inicio de sesión (token)
    permission_classes = (permissions.IsAuthenticated,)
    # Invocamos la petición GET para obtener todos los administradores
    def get(self, request, *args, **kwargs):
        admin = Administradores.objects.filter(user__is_active = True).order_by("id")
        lista = AdminSerializer(admin, many=True).data
        return Response(lista, 200)

class AdminView(generics.CreateAPIView):
    # Permisos por método (sobrescribe el comportamiento default)
    # Verifica que el usuario esté autenticado para las peticiones GET, PUT y DELETE
    def get_permissions(self):
        if self.request.method in ['GET', 'PUT', 'DELETE']:
            return [permissions.IsAuthenticated()]
        return []  # POST no requiere autenticación

    #Registrar nuevo usuario
    @transaction.atomic
    def post(self, request, *args, **kwargs):

        # Serializamos los datos de autenticación del administrador para volverlo de nuevo JSON
        user = UserSerializer(data=request.data)
        
        if user.is_valid():
            error = respuesta_faltantes(request.data, CAMPOS_USUARIO)
            if error:
                return error
            #Grabar datos del usuario --- esto va en la tabla authUser
            first_name = request.data['first_name']
            last_name = request.data['last_name']
            email = request.data['email']
            password = request.data['password']
            #Valida si existe el usuario o bien el email registrado
            if User.objects.filter(Q(email=email) | Q(username=email)).exists():
                return Response({"message":"El usuario "+email+" ya está registrado"},400)

            #Función para mandar a registrar a la BD
            user = User.objects.create( username = email,
                                        email = email,
                                        first_name = first_name,
                                        last_name = last_name,
                                        is_active = True)

            #Cifrar la contraseña
            user.set_password(password)
            user.save()

            #Se guarda en la BD el rol -> Administrador (lo define el servidor, no el cliente)
            group, created = Group.objects.get_or_create(name=ROL)
            group.user_set.add(user)

            #Almacenar los datos adicionales del administrador
            admin = Administradores.objects.create(user=user,
                                            clave_admin= request.data.get("clave_admin"),
                                            telefono= request.data.get("telefono"),
                                            rfc= mayusculas(request.data.get("rfc")),
                                            edad= request.data.get("edad"),
                                            ocupacion= request.data.get("ocupacion"))

            return Response({"Administrador creado correctamente": admin.id }, 201)

        return Response(user.errors, status=status.HTTP_400_BAD_REQUEST)
