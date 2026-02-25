from .models import Visitor

class TrackerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        ip = request.META.get('HTTP_X_FORWARDED_FOR')
        if ip:
            ip = ip.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        
        Visitor.objects.create(
            ip_address=ip,
            path=request.path,
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )

        response = self.get_response(request)
        return response