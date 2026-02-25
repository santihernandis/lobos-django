from django.db import models
import random
import string

class Sala(models.Model):
    codigo = models.CharField(max_length=6, unique=True, db_index=True)
    partida_iniciada = models.BooleanField(default=False)
    creada_en = models.DateTimeField(auto_now_add=True)
    configuracion_roles = models.JSONField(default=dict)
    
    def __str__(self):
        return f"Sala {self.codigo}"
    
    @staticmethod
    def generar_codigo():
        """Genera un código único de 6 caracteres"""
        while True:
            codigo = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            if not Sala.objects.filter(codigo=codigo).exists():
                return codigo
    
    def get_configuracion_default(self):
        """Configuración por defecto: 1 de cada rol"""
        return {
            'lobo': 1,
            'lobo_albino': 1,
            'lobo_padre': 1,
            'aldeano': 3,
            'arbol': 1,
            'cupido': 1,
            'bruja': 1,
            'nina_salvaje': 1,
            'cazador': 1,
            'vidente': 1,
        }
    
    def save(self, *args, **kwargs):
        # Inicializar configuración al crear
        if not self.pk and not self.configuracion_roles:
            self.configuracion_roles = self.get_configuracion_default()
        super().save(*args, **kwargs)

class Jugador(models.Model):
    ROLES = [
        ('lobo', 'Lobo'),
        ('lobo_albino', 'Lobo Albino'),
        ('lobo_padre', 'Lobo Padre'),
        ('aldeano', 'Aldeano'),
        ('arbol', 'Arbol'),
        ('cupido', 'Cupido'),
        ('bruja', 'Bruja'),
        ('nina_salvaje', 'Niña Salvaje'),
        ('cazador', 'Cazador'),
        ('vidente', 'Vidente'),
    ]
    
    # Usamos la session_key de Django para identificar el navegador del usuario
    session_id = models.CharField(max_length=40, unique=True)
    nombre = models.CharField(max_length=50) # El apodo que elijan para la partida
    rol = models.CharField(max_length=20, choices=ROLES, default='aldeano')
    esta_vivo = models.BooleanField(default=True)
    sala = models.ForeignKey(Sala, on_delete=models.CASCADE, related_name='jugadores', null=True)
    es_lider = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.nombre} ({self.sala.codigo if self.sala else 'Sin sala'})"
    
    class Meta:
        ordering = ['id']