__author__ = 'pwwpcheng'

from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect

def login_required(view_func):
    def check_login(request, *args,  **kwargs):
        if not request.user.is_authenticated():
            return redirect(settings.LOGIN_URL)
        return view_func(request, *args, **kwargs)
    return check_login


def admin_perm_required(view_func):
    def check_admin(request, *args, **kwargs):
        if request.user.has_perm('admin_permission'):
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, 'Permission denied: administrator permission needed')
            return redirect(request.META.get('HTTP_REFERER', '/'))
    return check_admin