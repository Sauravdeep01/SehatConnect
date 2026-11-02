from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from .forms import ReferralCreateForm, ReferralStatusUpdateForm
from .models import Referral
from accounts.decorators import health_worker_or_doctor_required, doctor_required
from accounts.models import User
from patients.models import Patient


@login_required
def referral_list(request):
    """View active and historical referral pathways"""
    user = request.user
    status = request.GET.get('status', '')
    urgency = request.GET.get('urgency', '')
    query = request.GET.get('q', '').strip()

    if user.is_admin_user:
        referrals = Referral.objects.all()
    elif user.role == User.ROLE_DOCTOR:
        doctor_profile = getattr(user, 'doctor_profile', None)
        hospital = doctor_profile.hospital if doctor_profile else None
        referrals = Referral.objects.filter(
            Q(assigned_doctor=user) | (Q(to_hospital=hospital) if hospital else Q()) | Q(referred_by=user)
        ).distinct()
    elif user.role == User.ROLE_HEALTH_WORKER:
        referrals = Referral.objects.filter(referred_by=user)
    else:
        referrals = Referral.objects.none()

    referrals = referrals.select_related('patient', 'from_hospital', 'to_hospital', 'target_specialty')

    if status:
        referrals = referrals.filter(status=status)
    if urgency:
        referrals = referrals.filter(urgency=urgency)
    if query:
        referrals = referrals.filter(
            Q(referral_code__icontains=query) |
            Q(patient__full_name__icontains=query) |
            Q(patient__registration_id__icontains=query) |
            Q(to_hospital__name__icontains=query)
        )

    paginator = Paginator(referrals, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'status': status,
        'urgency': urgency,
        'query': query,
        'status_choices': Referral.STATUS_CHOICES,
        'urgency_choices': Referral.URGENCY_CHOICES,
        'total_count': referrals.count(),
    }
    return render(request, 'referrals/referral_list.html', context)


@health_worker_or_doctor_required
def referral_create(request):
    """Initiate an inter-facility clinical referral"""
    patient_id = request.GET.get('patient_id')
    initial = {}
    if patient_id:
        initial['patient'] = get_object_or_404(Patient, pk=patient_id)

    if request.method == 'POST':
        form = ReferralCreateForm(request.POST)
        if form.is_valid():
            referral = form.save(commit=False)
            referral.referred_by = request.user
            if referral.transport_required:
                referral.transport_status = 'requested'
            referral.save()
            messages.success(
                request,
                f"Referral #{referral.referral_code} initiated successfully for {referral.patient.full_name}."
            )
            return redirect('referrals:referral_detail', pk=referral.pk)
    else:
        form = ReferralCreateForm(initial=initial)

    context = {
        'form': form,
        'title': 'Initiate Patient Referral / मरीज रेफरल प्रारंभ करें',
    }
    return render(request, 'referrals/referral_form.html', context)


@login_required
def referral_detail(request, pk):
    """Detailed tracker of referral lifecycle and clinical handoff"""
    referral = get_object_or_404(
        Referral.objects.select_related(
            'patient', 'from_hospital', 'to_hospital', 'target_specialty',
            'assigned_doctor', 'referred_by'
        ),
        pk=pk
    )

    can_update = False
    if request.user.is_admin_user:
        can_update = True
    elif request.user.role == User.ROLE_DOCTOR:
        doc_profile = getattr(request.user, 'doctor_profile', None)
        if doc_profile and doc_profile.hospital_id == referral.to_hospital_id:
            can_update = True
        elif referral.assigned_doctor == request.user:
            can_update = True

    status_form = ReferralStatusUpdateForm(instance=referral) if can_update else None

    context = {
        'referral': referral,
        'can_update': can_update,
        'status_form': status_form,
    }
    return render(request, 'referrals/referral_detail.html', context)


@doctor_required
def referral_update_status(request, pk):
    """Receiving doctor/hospital staff updates referral status and bed admission remarks"""
    referral = get_object_or_404(Referral, pk=pk)
    
    if request.method == 'POST':
        form = ReferralStatusUpdateForm(request.POST, instance=referral)
        if form.is_valid():
            ref = form.save()
            messages.success(request, f"Referral #{ref.referral_code} status updated to {ref.get_status_display()}.")
            return redirect('referrals:referral_detail', pk=ref.pk)

    return redirect('referrals:referral_detail', pk=referral.pk)
