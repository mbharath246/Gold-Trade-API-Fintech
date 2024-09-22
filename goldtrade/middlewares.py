from django.core.cache import cache
from django.http import JsonResponse

class RateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.cooldown_period = 60 
        self.max_requests = 5

    def __call__(self, request):
        user_id = request.user.id if request.user.is_authenticated else 'anonymous'
        cache_key = f'rate_limit_{user_id}'
        request_count = cache.get(cache_key, 0)

        if request_count >= self.max_requests:
            return JsonResponse({'error': 'Too many requests. Please wait a moment and try again after 60 seconds.'}, status=429)

        cache.set(cache_key, request_count + 1, timeout=self.cooldown_period)

        response = self.get_response(request)

        return response
