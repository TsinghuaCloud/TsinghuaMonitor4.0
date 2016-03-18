__author__ = 'pwwpcheng'

from django.conf import settings
from django.shortcuts import redirect

def enforce_login_decorator(view_func):
    def check_login(request, **kwargs):
        if not request.user.is_authenticated():
            return redirect(settings.LOGIN_URL)
        return view_func(request, **kwargs)
    return check_login

