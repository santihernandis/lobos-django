from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('unirse/<str:codigo_sala>/', views.unirse_directo, name='unirse_directo'),
    path('pre_lobby/', views.pre_lobby, name='pre_lobby'),
    path('lobby/<str:codigo_sala>/', views.lobby, name='lobby'),
    path('iniciar_partida/<str:codigo_sala>/', views.iniciar_partida, name='iniciar_partida'),
    path('guardar_configuracion/<str:codigo_sala>/', views.guardar_configuracion_roles, name='guardar_configuracion'),
]