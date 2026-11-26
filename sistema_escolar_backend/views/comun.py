from datetime import datetime

from django.utils import timezone
from django.utils.dateparse import parse_date, parse_datetime
from rest_framework.response import Response

CAMPOS_USUARIO = ["first_name", "last_name", "email", "password"]


def campos_faltantes(data, campos):
    return [c for c in campos if data.get(c) in (None, "")]


def respuesta_faltantes(data, campos):
    # Devuelve un 400 con los campos que faltan, o None si todo viene completo
    faltan = campos_faltantes(data, campos)
    if faltan:
        return Response({"message": "Faltan campos obligatorios: " + ", ".join(faltan)}, 400)
    return None


def a_fecha(valor):
    # Convierte "2000-01-01" o ISO 8601 a datetime con zona horaria.
    # Lanza ValueError si la fecha es inválida
    if valor in (None, ""):
        return None
    fecha = parse_datetime(str(valor))
    if fecha is None:
        solo_fecha = parse_date(str(valor))
        if solo_fecha is None:
            raise ValueError("Fecha inválida: " + str(valor))
        fecha = datetime.combine(solo_fecha, datetime.min.time())
    if timezone.is_naive(fecha):
        fecha = timezone.make_aware(fecha)
    return fecha


def mayusculas(valor):
    return valor.upper() if isinstance(valor, str) else valor
