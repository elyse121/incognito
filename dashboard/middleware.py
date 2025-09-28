from django.shortcuts import redirect
from .models import ManageMember

class BanCheckMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            try:
                member = ManageMember.objects.get(member=request.user)
                if not member.status:  # banned
                    from django.contrib.auth import logout
                    logout(request)
                    return redirect("banned_account_page")
            except ManageMember.DoesNotExist:
                pass
        return self.get_response(request)
