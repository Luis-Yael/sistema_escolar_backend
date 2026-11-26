from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views.bootstrap import VersionView
from sistema_escolar_backend.views import administradores
from sistema_escolar_backend.views import auth
from sistema_escolar_backend.views import alumnos
from sistema_escolar_backend.views import maestros

urlpatterns = [
    #Panel de administración de Django
        path('panel/', admin.site.urls),
    #Create Admin
        path('admin/', administradores.AdminView.as_view()),
    #Admin Data
        path('lista-admins/', administradores.AdminAll.as_view()),
    #Edit Admin
        #path('admins-edit/', administradores.AdminsViewEdit.as_view())
    #Create Alumno
        path('alumnos/', alumnos.AlumnosView.as_view()),
    #Alumno Data
        path('lista-alumnos/', alumnos.AlumnosAll.as_view()),
    #Create Maestro
        path('maestros/', maestros.MaestrosView.as_view()),
    #Maestro Data
        path('lista-maestros/', maestros.MaestrosAll.as_view()),
    # #Total Users
    #     path('total-usuarios/', administradores.TotalUsers.as_view()),
    #Login
        path('login/', auth.CustomAuthToken.as_view()),
    #Logout
        path('logout/', auth.Logout.as_view())
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
