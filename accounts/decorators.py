from functools import wraps
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


def health_worker_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.role == 'health_worker' or request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        messages.error(request, "Access restricted. This section is reserved for Community Health Workers (ASHA/ANM).")
        return redirect('accounts:dashboard_redirect')
    return wrapper


def doctor_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.role == 'doctor' or request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        messages.error(request, "Access restricted. This section is reserved for Doctors and Hospital Medical Staff.")
        return redirect('accounts:dashboard_redirect')
    return wrapper


def admin_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.role == 'admin' or request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        messages.error(request, "Access restricted. Administrator privileges required.")
        return redirect('accounts:dashboard_redirect')
    return wrapper


def health_worker_or_doctor_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.role in ['health_worker', 'doctor', 'admin'] or request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        messages.error(request, "You do not have authorization to view this clinical record.")
        return redirect('accounts:dashboard_redirect')
    return wrapper
