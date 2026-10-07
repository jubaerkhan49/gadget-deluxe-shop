from .models import PageVisit


class VisitorAnalyticsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Track only public front-end page GET requests (skip static, media, admin, dashboard)
        if request.method == 'GET' and response.status_code == 200:
            path = request.path
            ignored_prefixes = ['/static/', '/media/', '/admin/', '/shop-admin/', '/favicon.ico']
            
            if not any(path.startswith(prefix) for prefix in ignored_prefixes):
                try:
                    # Get client IP
                    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
                    if x_forwarded_for:
                        ip = x_forwarded_for.split(',')[0].strip()
                    else:
                        ip = request.META.get('REMOTE_ADDR')

                    session_key = request.session.session_key
                    if not session_key:
                        request.session.save()
                        session_key = request.session.session_key

                    user = request.user if request.user.is_authenticated else None
                    user_agent = request.META.get('HTTP_USER_AGENT', '')[:250]
                    referer = request.META.get('HTTP_REFERER', '')[:250]

                    PageVisit.objects.create(
                        ip_address=ip,
                        session_key=session_key,
                        path=path[:250],
                        user_agent=user_agent,
                        referer=referer,
                        user=user
                    )
                except Exception:
                    # Suppress any analytics logging failure so customer requests are never impacted
                    pass

        return response
