from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from .forms import PatientForm, PatientVitalForm
from .models import Patient, PatientVital
from accounts.decorators import health_worker_required, health_worker_or_doctor_required


@health_worker_or_doctor_required
def patient_list(request):
    """List and search patients with filters"""
    query = request.GET.get('q', '').strip()
    gender = request.GET.get('gender', '')
    village = request.GET.get('village', '').strip()
    blood_group = request.GET.get('blood_group', '')

    patients = Patient.objects.all().select_related('registered_by')

    # If Health Worker, emphasize/prioritize or filter by their village/registration
    if request.user.role == 'health_worker' and not request.user.is_superuser:
        # Show their own registered patients or allow search across system
        show_all = request.GET.get('all', '0') == '1'
        if not show_all and not query:
            patients = patients.filter(registered_by=request.user)

    if query:
        patients = patients.filter(
            Q(full_name__icontains=query) |
            Q(registration_id__icontains=query) |
            Q(phone__icontains=query) |
            Q(abha_id__icontains=query) |
            Q(village__icontains=query)
        )

    if gender:
        patients = patients.filter(gender=gender)

    if village:
        patients = patients.filter(village__icontains=village)

    if blood_group:
        patients = patients.filter(blood_group=blood_group)

    paginator = Paginator(patients, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'query': query,
        'gender': gender,
        'village': village,
        'blood_group': blood_group,
        'total_count': patients.count(),
    }
    return render(request, 'patients/patient_list.html', context)


@health_worker_or_doctor_required
def patient_detail(request, pk):
    """Detailed health dossier of a rural patient"""
    patient = get_object_or_404(Patient, pk=pk)
    vitals_history = patient.vitals.all().order_by('-recorded_at')[:10]
    appointments = patient.appointments.all().select_related('doctor', 'hospital').order_by('-appointment_date')
    referrals = patient.referrals.all().select_related('to_hospital', 'target_specialty').order_by('-created_at')

    context = {
        'patient': patient,
        'vitals_history': vitals_history,
        'appointments': appointments,
        'referrals': referrals,
        'vital_form': PatientVitalForm(),
    }
    return render(request, 'patients/patient_detail.html', context)


@health_worker_required
def patient_create(request):
    """Health worker registers a new patient"""
    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            patient = form.save(commit=False)
            patient.registered_by = request.user
            # Auto-fill village/block from worker profile if empty
            worker_profile = getattr(request.user, 'health_worker_profile', None)
            if worker_profile:
                if not patient.village:
                    patient.village = worker_profile.assigned_village
                if not patient.block:
                    patient.block = worker_profile.block
                if not patient.district:
                    patient.district = worker_profile.district
            patient.save()
            messages.success(request, f"Patient {patient.full_name} registered successfully with ID: {patient.registration_id}")
            return redirect('patients:patient_detail', pk=patient.pk)
    else:
        initial = {}
        worker_profile = getattr(request.user, 'health_worker_profile', None)
        if worker_profile:
            initial = {
                'village': worker_profile.assigned_village,
                'panchayat': worker_profile.panchayat,
                'block': worker_profile.block,
                'district': worker_profile.district,
                'state': worker_profile.state,
            }
        form = PatientForm(initial=initial)

    context = {
        'form': form,
        'title': 'Register New Patient / नया मरीज पंजीयन',
    }
    return render(request, 'patients/patient_form.html', context)


@health_worker_required
def patient_update(request, pk):
    """Update patient demographic and medical details"""
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == 'POST':
        form = PatientForm(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            messages.success(request, f"Patient records for {patient.full_name} updated successfully.")
            return redirect('patients:patient_detail', pk=patient.pk)
    else:
        form = PatientForm(instance=patient)

    context = {
        'form': form,
        'patient': patient,
        'title': f'Update Patient: {patient.full_name}',
    }
    return render(request, 'patients/patient_form.html', context)


@health_worker_or_doctor_required
def patient_vitals_add(request, pk):
    """Record health vitals (BP, SpO2, Blood Sugar, Temperature, etc.)"""
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == 'POST':
        form = PatientVitalForm(request.POST)
        if form.is_valid():
            vital = form.save(commit=False)
            vital.patient = patient
            vital.recorded_by = request.user
            vital.save()
            messages.success(request, f"Vitals recorded for {patient.full_name}.")
            return redirect('patients:patient_detail', pk=patient.pk)
        else:
            messages.error(request, "Failed to record vitals. Please check the values entered.")
    return redirect('patients:patient_detail', pk=patient.pk)


@health_worker_required
def patient_delete(request, pk):
    """Remove patient record"""
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == 'POST':
        name = patient.full_name
        patient.delete()
        messages.success(request, f"Patient record '{name}' has been deleted.")
        return redirect('patients:patient_list')
    return render(request, 'patients/patient_confirm_delete.html', {'patient': patient})
