from django.urls import path
from . import views

urlpatterns = [
    # ── Autenticación ──────────────────────────────────────────
    path('',              views.login_view,        name='login'),
    path('registro/',     views.registro_view,     name='registro'),
    path('admin-panel/',  views.admin_view,         name='admin_panel'),

    # ── Perfil ─────────────────────────────────────────────────
    path('perfil/',       views.perfil_view,        name='perfil'),

    # ── Proceso de selección ───────────────────────────────────
    path('postulacion/',  views.postulacion_view,   name='postulacion'),
    path('seleccion/',    views.seleccion_view,     name='seleccion'),
    path('evaluar-cv/',   views.evaluar_cv_view,    name='evaluar_cv'),

    # ── Evaluaciones de desempeño ──────────────────────────────
    path('evaluaciones/', views.evaluaciones_view,  name='evaluaciones'),

    # ── Capacitaciones ─────────────────────────────────────────
    path('capacitaciones/', views.capacitaciones_view, name='capacitaciones'),
]