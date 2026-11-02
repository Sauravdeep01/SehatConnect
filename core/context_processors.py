from core.translations import TRANSLATIONS
from appointments.models import Appointment
from patients.models import Patient
from referrals.models import Referral
from hospitals.models import Hospital


def language_processor(request):
    """Provides current language code and translation strings to all templates"""
    lang = request.session.get('language', 'en')
    if lang not in TRANSLATIONS:
        lang = 'en'
    
    t_dict = TRANSLATIONS[lang]
    alt_lang = 'hi' if lang == 'en' else 'en'
    alt_lang_name = 'हिन्दी' if lang == 'en' else 'English'
    
    return {
        'current_language': lang,
        'alt_language': alt_lang,
        'alt_language_name': alt_lang_name,
        't': t_dict,
        'is_hindi': (lang == 'hi'),
    }


def global_stats_processor(request):
    """Provides global counts and user-specific badge counters to templates"""
    context = {
        'total_patients_count': 0,
        'total_hospitals_count': 0,
        'total_appointments_count': 0,
        'total_referrals_count': 0,
        'user_pending_appointments_count': 0,
        'user_pending_referrals_count': 0,
    }
    
    try:
        context['total_patients_count'] = Patient.objects.count()
        context['total_hospitals_count'] = Hospital.objects.filter(is_verified=True).count()
        context['total_appointments_count'] = Appointment.objects.count()
        context['total_referrals_count'] = Referral.objects.count()

        if request.user.is_authenticated:
            if request.user.role == 'doctor':
                context['user_pending_appointments_count'] = Appointment.objects.filter(
                    doctor=request.user,
                    status='pending'
                ).count()
                context['user_pending_referrals_count'] = Referral.objects.filter(
                    assigned_doctor=request.user,
                    status='pending'
                ).count()
            elif request.user.role == 'health_worker':
                context['user_pending_appointments_count'] = Appointment.objects.filter(
                    booked_by=request.user,
                    status='pending'
                ).count()
                context['user_pending_referrals_count'] = Referral.objects.filter(
                    referred_by=request.user,
                    status='pending'
                ).count()
    except Exception:
        pass
        
    return context
