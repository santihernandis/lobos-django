import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Sala, Jugador

class LobbyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.codigo_sala = self.scope['url_route']['kwargs']['codigo_sala']
        self.room_group_name = f'lobby_{self.codigo_sala}'

        # Unirse al grupo de la sala
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        
        # Notificar a todos que un jugador conectó (para actualizar la lista)
        jugadores = await self.get_jugadores()
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'actualizar_jugadores',
                'jugadores': jugadores
            }
        )

    async def disconnect(self, close_code):
        # Salir del grupo
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        tipo = data.get('tipo')

        if tipo == 'jugador_unido':
            # Obtener lista actualizada de jugadores
            jugadores = await self.get_jugadores()
            
            # Enviar a todos en el grupo
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'actualizar_jugadores',
                    'jugadores': jugadores
                }
            )
        
        elif tipo == 'partida_iniciada':
            # Notificar a todos que la partida comenzó
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'iniciar_juego',
                    'codigo_sala': self.codigo_sala
                }
            )
        
        elif tipo == 'configuracion_actualizada':
            # Obtener configuración actualizada
            configuracion = await self.get_configuracion_roles()
            
            # Enviar a todos en el grupo
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'actualizar_configuracion',
                    'configuracion': configuracion
                }
            )

    async def actualizar_jugadores(self, event):
        # Enviar lista de jugadores al WebSocket
        await self.send(text_data=json.dumps({
            'tipo': 'actualizar_jugadores',
            'jugadores': event['jugadores']
        }))

    async def iniciar_juego(self, event):
        # Notificar que la partida ha comenzado
        await self.send(text_data=json.dumps({
            'tipo': 'partida_iniciada',
            'codigo_sala': event['codigo_sala']
        }))
    
    async def actualizar_configuracion(self, event):
        # Enviar configuración actualizada al WebSocket
        await self.send(text_data=json.dumps({
            'tipo': 'configuracion_actualizada',
            'configuracion': event['configuracion']
        }))

    @database_sync_to_async
    def get_jugadores(self):
        """Obtiene la lista de jugadores de la sala con sus roles"""
        try:
            sala = Sala.objects.get(codigo=self.codigo_sala)
            jugadores = sala.jugadores.all().values('nombre', 'es_lider', 'rol')
            return list(jugadores)
        except Sala.DoesNotExist:
            return []
    
    @database_sync_to_async
    def get_configuracion_roles(self):
        """Obtiene la configuración de roles de la sala"""
        try:
            sala = Sala.objects.get(codigo=self.codigo_sala)
            return sala.configuracion_roles or sala.get_configuracion_default()
        except Sala.DoesNotExist:
            return {}
