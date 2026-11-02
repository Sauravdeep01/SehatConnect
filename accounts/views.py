from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .decorators import health_worker_required, doctor_required, admin_required
from .forms import LoginForm, UserProfileUpdateForm, HealthWorkerProfileForm, DoctorProfileForm
from .models import User, HealthWorkerProfile, DoctorProfile
from appointments.models import Appointment
from patients.models import Patient
from referrals.models import Referral
from hospitals.models import Hospital


def login_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard_redirect')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            login(request, user)
            messages.success(request, f"Welcome back, {user.get_full_name() or user.username}!")
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('accounts:dashboard_redirect')
    else:
        form = LoginForm()
    
    context = {'form': form}
    return render(request, 'accounts/login.html', context)


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out securely.")
    return redirect('core:home')


@login_required
def dashboard_redirect(request):
    """Directs authenticated users to their specific role dashboard"""
    if request.user.is_admin_user:
        return redirect('analytics:admin_dashboard')
    elif request.user.role == User.ROLE_DOCTOR:
        return redirect('accounts:doctor_dashboard')
    elif request.user.role == User.ROLE_HEALTH_WORKER:
        return redirect('accounts:worker_dashboard')
    return redirect('core:home')


@health_worker_required
def worker_dashboard(request):
    """Health Worker / ASHA Command Center"""
    user = request.user
    today = timezone.now().date()
    
    # Patients managed by this worker
    my_patients = Patient.objects.filter(registered_by=user).order_by('-created_at')
    patients_count = my_patients.count()
    
    # Appointments booked by this worker
    my_appointments = Appointment.objects.filter(booked_by=user).select_related('patient', 'doctor', 'hospital')
    today_appointments = my_appointments.filter(appointment_date=today)
    upcoming_appointments = my_appointments.filter(appointment_date__gte=today).exclude(status__in=['completed', 'cancelled'])[:5]
    
    # Referrals initiated
    my_referrals = Referral.objects.filter(referred_by=user).select_related('patient', 'to_hospital', 'target_specialty')[:5]
    pending_referrals_count = Referral.objects.filter(referred_by=user, status='pending').count()
    
    # Counts
    stats = {
        'total_patients': patients_count,
        'active_appointments': my_appointments.filter(status__in=['pending', 'confirmed']).count(),
        'today_appointments_count': today_appointments.count(),
        'pending_referrals': pending_referrals_count,
    }
    
    context = {
        'stats': stats,
        'recent_patients': my_patients[:6],
        'upcoming_appointments': upcoming_appointments,
        'today_appointments': today_appointments,
        'recent_referrals': my_referrals,
        'today': today,
    }
    return render(request, 'accounts/worker_dashboard.html', context)


@doctor_required
def doctor_dashboard(request):
    """Doctor / Hospital Staff OPD Command Center"""
    user = request.user
    today = timezone.now().date()
    
    # Doctor's profile & hospital
    doctor_profile = getattr(user, 'doctor_profile', None)
    hospital = doctor_profile.hospital if doctor_profile else None
    
    # Appointments for this doctor
    doctor_appts = Appointment.objects.filter(doctor=user).select_related('patient', 'hospital', 'booked_by')
    today_queue = doctor_appts.filter(appointment_date=today).order_by('token_number')
    
    pending_requests = doctor_appts.filter(status='pending').order_by('appointment_date')[:10]
    upcoming_appts = doctor_appts.filter(appointment_date__gt=today).exclude(status__in=['cancelled', 'completed'])[:10]
    
    # Referrals directed to this doctor or hospital
    referrals_query = Referral.objects.filter(
        Q(assigned_doctor=user) | (Q(to_hospital=hospital) if hospital else Q())
    ).select_related('patient', 'from_hospital', 'target_specialty').distinct()
    
    incoming_referrals = referrals_query.filter(status__in=['pending', 'accepted', 'in_transit'])[:8]
    
    # Metrics
    stats = {
        'today_total': today_queue.count(),
        'today_pending': today_queue.filter(status='pending').count(),
        'today_completed': today_queue.filter(status='completed').count(),
        'incoming_referrals_count': incoming_referrals.count(),
    }
    
    context = {
        'stats': stats,
        'today_queue': today_queue,
        'pending_requests': pending_requests,
        'upcoming_appts': upcoming_appts,
        'incoming_referrals': incoming_referrals,
        'doctor_profile': doctor_profile,
        'hospital': hospital,
        'today': today,
    }
    return render(request, 'accounts/doctor_dashboard.html', context)


@doctor_required
def toggle_availability(request):
    """Doctor toggles active OPD availability status"""
    doctor_profile = getattr(request.user, 'doctor_profile', None)
    if doctor_profile:
        doctor_profile.is_available = not doctor_profile.is_available
        doctor_profile.save()
        status_str = "Available / उपलब्ध" if doctor_profile.is_available else "On Leave / अनुपलब्ध"
        messages.success(request, f"Your OPD status is now set to: {status_str}")
    return redirect('accounts:doctor_dashboard')


@login_required
def profile_view(request):
    """View and update profile information"""
    user = request.user
    user_form = UserProfileUpdateForm(instance=user)
    profile_form = None
    
    if user.role == User.ROLE_HEALTH_WORKER:
        worker_profile, _ = HealthWorkerProfile.objects.get_or_create(user=user)
        profile_form = HealthWorkerProfileForm(instance=worker_profile)
    elif user.role == User.ROLE_DOCTOR:
        doc_profile, _ = DoctorProfile.objects.get_or_create(
            user=user,
            defaults={'license_number': f'MED-{user.id:04d}'}
        )
        profile_form = DoctorProfileForm(instance=doc_profile)
        
    if request.method == 'POST':
        user_form = UserProfileUpdateForm(request.POST, instance=user)
        if user_form.is_valid():
            user_form.save()
            
            if user.role == User.ROLE_HEALTH_WORKER:
                worker_profile = user.health_worker_profile
                profile_form = HealthWorkerProfileForm(request.POST, instance=worker_profile)
                if profile_form.is_valid():
                    profile_form.save()
            elif user.role == User.ROLE_DOCTOR:
                doc_profile = user.doctor_profile
                profile_form = DoctorProfileForm(request.POST, instance=doc_profile)
                if profile_form.is_valid():
                    profile_form.save()
                    
            messages.success(request, "Profile updated successfully.")
            return redirect('accounts:profile')
            
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'accounts/profile.html', context)
