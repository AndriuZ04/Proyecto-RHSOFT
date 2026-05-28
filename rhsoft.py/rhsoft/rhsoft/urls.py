from django.urls import path, include

urlpatterns = [
    path('',         include('asistencia.urls')),
    # Agrega aquí los urls de tus compañeros, ej:
    # path('nomina/',  include('nomina.urls')),
    # path('sst/',     include('sst.urls')),
]
