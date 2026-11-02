import json
from datetime import timedelta
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, Sum
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from accounts.decorators import admin_required
from accounts.models import User, HealthWorkerProfile, DoctorProfile
from appointments.models import Appointment
from hospitals.models import Hospital, Specialty
from patients.models import Patient
from referrals.models import Referral


@admin_required
def admin_dashboard(request):
    """Central Administrative and Analytics Command Dashboard with Chart.js datasets"""
    today = timezone.now().date()
    seven_days_ago = today - timedelta(days=6)

    # 1. Headline KPIs
    total_patients = Patient.objects.count()
    total_hospitals = Hospital.objects.count()
    verified_hospitals = Hospital.objects.filter(is_verified=True).count()
    total_appointments = Appointment.objects.count()
    today_appointments = Appointment.objects.filter(appointment_date=today).count()
    total_referrals = Referral.objects.count()
    emergency_referrals = Referral.objects.filter(urgency='emergency', status__in=['pending', 'accepted', 'in_transit']).count()
    
    total_health_workers = User.objects.filter(role=User.ROLE_HEALTH_WORKER).count()
    total_doctors = User.objects.filter(role=User.ROLE_DOCTOR).count()

    # Bed Capacity stats
    bed_stats = Hospital.objects.aggregate(
        total=Sum('total_beds'),
        available=Sum('available_beds'),
        icu=Sum('icu_beds')
    )
    total_beds = bed_stats['total'] or 0
    available_beds = bed_stats['available'] or 0
    occupied_beds = max(0, total_beds - available_beds)
    bed_occupancy_rate = round((occupied_beds / total_beds * 100), 1) if total_beds > 0 else 0

    # 2. Chart.js Data: Appointments Last 7 Days
    date_labels = []
    appointment_counts = []
    for i in range(7):
        day = seven_days_ago + timedelta(days=i)
        date_labels.append(day.strftime('%d %b'))
        cnt = Appointment.objects.filter(appointment_date=day).count()
        appointment_counts.append(cnt)

    # 3. Chart.js Data: Referral Status Breakdown
    referral_status_counts = Referral.objects.values('status').annotate(total=Count('id'))
    status_map = dict(Referral.STATUS_CHOICES)
    ref_labels = []
    ref_data = []
    for item in referral_status_counts:
        label = status_map.get(item['status'], item['status']).split(' / ')[0]
        ref_labels.append(label)
        ref_data.append(item['total'])
    if not ref_labels:
        ref_labels = ['Pending', 'Accepted', 'Completed']
        ref_data = [0, 0, 0]

    # 4. Chart.js Data: Facility Types
    facility_counts = Hospital.objects.values('facility_type').annotate(total=Count('id'))
    facility_map = dict(Hospital.FACILITY_TYPES)
    hosp_labels = []
    hosp_data = []
    for item in facility_counts:
        hosp_labels.append(facility_map.get(item['facility_type'], item['facility_type']).split(' / ')[0])
        hosp_data.append(item['total'])

    # 5. Chart.js Data: Patient Gender Demographics
    gender_counts = Patient.objects.values('gender').annotate(total=Count('id'))
    gender_labels = [g['gender'].capitalize() for g in gender_counts]
    gender_data = [g['total'] for g in gender_counts]

    # Recent Records
    recent_appointments = Appointment.objects.select_related('patient', 'doctor', 'hospital').order_by('-created_at')[:6]
    recent_referrals = Referral.objects.select_related('patient', 'to_hospital').order_by('-created_at')[:5]
    unverified_hospitals = Hospital.objects.filter(is_verified=False)

    context = {
        'total_patients': total_patients,
        'total_hospitals': total_hospitals,
        'verified_hospitals': verified_hospitals,
        'total_appointments': total_appointments,
        'today_appointments': today_appointments,
        'total_referrals': total_referrals,
        'emergency_referrals': emergency_referrals,
        'total_health_workers': total_health_workers,
        'total_doctors': total_doctors,
        'total_beds': total_beds,
        'available_beds': available_beds,
        'bed_occupancy_rate': bed_occupancy_rate,
        
        # Chart JSON objects
        'chart_date_labels': json.dumps(date_labels),
        'chart_appointment_counts': json.dumps(appointment_counts),
        'chart_ref_labels': json.dumps(ref_labels),
        'chart_ref_data': json.dumps(ref_data),
        'chart_hosp_labels': json.dumps(hosp_labels),
        'chart_hosp_data': json.dumps(hosp_data),
        'chart_gender_labels': json.dumps(gender_labels),
        'chart_gender_data': json.dumps(gender_data),

        # Recent activities
        'recent_appointments': recent_appointments,
        'recent_referrals': recent_referrals,
        'unverified_hospitals': unverified_hospitals,
    }
    return render(request, 'analytics/admin_dashboard.html', context)


@admin_required
def admin_verify_hospital(request, pk):
    """Toggle hospital verification status"""
    hospital = get_object_or_404(Hospital, pk=pk)
    hospital.is_verified = not hospital.is_verified
    hospital.save()
    status_str = "Verified / सत्यापित" if hospital.is_verified else "Unverified / असत्यापित"
    messages.success(request, f"Hospital '{hospital.name}' is now marked as {status_str}.")
    return redirect('analytics:admin_dashboard')


@admin_required
def admin_users_list(request):
    """User Management directory for Admins"""
    role = request.GET.get('role', '')
    query = request.GET.get('q', '').strip()

    users = User.objects.all().order_by('-date_joined')
    if role:
        users = users.filter(role=role)
    if query:
        users = users.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(phone_number__icontains=query)
        )

    context = {
        'users': users,
        'role': role,
        'query': query,
        'total_count': users.count(),
    }
    return render(request, 'analytics/admin_users_list.html', context)


@admin_required
def admin_user_toggle_active(request, pk):
    """Toggle user active status"""
    user = get_object_or_404(User, pk=pk)
    if user == request.user:
        messages.error(request, "You cannot deactivate your own administrative account.")
    else:
        user.is_active = not user.is_active
        user.save()
        status_str = "Activated" if user.is_active else "Deactivated"
        messages.success(request, f"User {user.username} has been {status_str}.")
    return redirect('analytics:admin_users_list')
