from django.urls import path
from . import views

urlpatterns = [
    path('',        views.login_view,  name='login'),
    path('registro/', views.registro_view, name='registro'),
    path('admin-panel/', views.admin_view, name='admin_panel'),
]
