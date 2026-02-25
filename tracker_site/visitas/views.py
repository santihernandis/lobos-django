from django.shortcuts import render
from .models import Visitor
import json
from django.http import JsonResponse
from django.utils import timezone

def home(request):
    return render(request, 'visitas/home.html', {})

def registrar_fingerprint(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        fingerprint = data.get('fingerprint')
        ip_address = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR'))
        user_agent = request.META.get('HTTP_USER_AGENT', '')

        visitor, created = Visitor.objects.get_or_create(
            fingerprint=fingerprint,
            defaults={'ip_address': ip_address, 'user_agent': user_agent}
        )

        if not created:
            visitor.ultima_visita = timezone.now()
            visitor.save()
        
        return JsonResponse({'status': 'ok', 'new': created})
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)