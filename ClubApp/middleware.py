from django.http import HttpResponse
from django.contrib.auth import get_user_model
from django.utils.deprecation import MiddlewareMixin

class CheckUserMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
            User = get_user_model()
            try:
                User.objects.get(pk=request.user.pk)
            except User.DoesNotExist:
                return HttpResponse("You are not allowed to see this page", status=403)
        return None
