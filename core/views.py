from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from appointments.models import Appointment
from hospitals.models import Hospital
from patients.models import Patient
from referrals.models import Referral


def home(request):
    """Modern public landing page for rural citizens & health workers"""
    featured_hospitals = Hospital.objects.filter(is_verified=True).prefetch_related('specialties')[:6]
    recent_updates = Appointment.objects.filter(status='confirmed').order_by('-updated_at')[:4]
    
    context = {
        'featured_hospitals': featured_hospitals,
        'recent_updates': recent_updates,
    }
    return render(request, 'core/home.html', context)


def about(request):
    """About SehatConnect rural public healthcare platform"""
    return render(request, 'core/about.html')


def contact(request):
    """Helplines, emergency services (108/104), and district CMO contacts"""
    return render(request, 'core/contact.html')


def set_language(request, lang_code):
    """Switch language between English ('en') and Hindi ('hi')"""
    if lang_code in ['en', 'hi']:
        request.session['language'] = lang_code
    
    next_url = request.GET.get('next') or request.META.get('HTTP_REFERER') or '/'
    return redirect(next_url)
