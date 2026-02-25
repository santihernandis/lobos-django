from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('api/fingerprint/', views.registrar_fingerprint, name='registrar_fingerprint'),
]