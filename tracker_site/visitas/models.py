from django.db import models

class Visitor(models.Model):
    fingerprint = models.CharField(max_length=128, unique=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.CharField(max_length=255)
    primera_visita = models.DateTimeField(auto_now_add=True)
    ultima_visita = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.fingerprint} ({self.ip_address})"
