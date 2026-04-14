"""
Custom decorators for role-based access control.
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def admin_required(view_func):
    """Decorator to restrict access to admin users only."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please login to access this page.')
            return redirect('login')
        if not request.user.is_admin:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('dashboard_redirect')
        return view_func(request, *args, **kwargs)
    return wrapper


def donor_required(view_func):
    """Decorator to restrict access to donor users only."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please login to access this page.')
            return redirect('login')
        if not request.user.is_donor:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('dashboard_redirect')
        return view_func(request, *args, **kwargs)
    return wrapper


def patient_required(view_func):
    """Decorator to restrict access to patient users only."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please login to access this page.')
            return redirect('login')
        if not request.user.is_patient_user:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('dashboard_redirect')
        return view_func(request, *args, **kwargs)
    return wrapper


def admin_or_donor_required(view_func):
    """Decorator to restrict access to admin or donor users."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please login to access this page.')
            return redirect('login')
        if not (request.user.is_admin or request.user.is_donor):
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('dashboard_redirect')
        return view_func(request, *args, **kwargs)
    return wrapper


def admin_or_patient_required(view_func):
    """Decorator to restrict access to admin or patient users."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please login to access this page.')
            return redirect('login')
        if not (request.user.is_admin or request.user.is_patient_user):
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('dashboard_redirect')
        return view_func(request, *args, **kwargs)
    return wrapper
