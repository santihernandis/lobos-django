from django.contrib import admin
from .models import Jugador, Sala

@admin.register(Sala)
class SalaAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'partida_iniciada', 'creada_en', 'num_jugadores')
    list_filter = ('partida_iniciada', 'creada_en')
    search_fields = ('codigo',)
    readonly_fields = ('creada_en',)
    
    def num_jugadores(self, obj):
        return obj.jugadores.count()
    num_jugadores.short_description = 'Jugadores'

@admin.register(Jugador)
class JugadorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'rol', 'esta_vivo', 'es_lider', 'sala', 'session_id')
    list_filter = ('rol', 'esta_vivo', 'es_lider', 'sala')
    search_fields = ('nombre', 'session_id')
    list_select_related = ('sala',)
