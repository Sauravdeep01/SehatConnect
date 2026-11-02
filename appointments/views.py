from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .forms import AppointmentBookingForm, AppointmentConsultationForm, AppointmentRescheduleForm
from .models import Appointment
from accounts.decorators import health_worker_required, doctor_required, health_worker_or_doctor_required
from accounts.models import User
from hospitals.models import Hospital
from patients.models import Patient


@login_required
def appointment_list(request):
    """List appointments tailored to the user's role with filter options"""
    user = request.user
    status = request.GET.get('status', '')
    urgency = request.GET.get('urgency', '')
    date_filter = request.GET.get('date', '')
    query = request.GET.get('q', '').strip()

    if user.is_admin_user:
        appointments = Appointment.objects.all()
    elif user.role == User.ROLE_DOCTOR:
        appointments = Appointment.objects.filter(doctor=user)
    elif user.role == User.ROLE_HEALTH_WORKER:
        appointments = Appointment.objects.filter(booked_by=user)
    else:
        appointments = Appointment.objects.none()

    appointments = appointments.select_related('patient', 'doctor', 'hospital')

    if status:
        appointments = appointments.filter(status=status)
    if urgency:
        appointments = appointments.filter(urgency=urgency)
    if date_filter:
        appointments = appointments.filter(appointment_date=date_filter)
    if query:
        appointments = appointments.filter(
            Q(appointment_number__icontains=query) |
            Q(patient__full_name__icontains=query) |
            Q(patient__registration_id__icontains=query) |
            Q(hospital__name__icontains=query)
        )

    paginator = Paginator(appointments, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'status': status,
        'urgency': urgency,
        'date_filter': date_filter,
        'query': query,
        'status_choices': Appointment.STATUS_CHOICES,
        'urgency_choices': Appointment.URGENCY_CHOICES,
        'total_count': appointments.count(),
    }
    return render(request, 'appointments/appointment_list.html', context)


@health_worker_required
def appointment_book(request):
    """Health worker books an OPD appointment for a rural patient"""
    patient_id = request.GET.get('patient_id')
    hospital_id = request.GET.get('hospital_id')
    doctor_id = request.GET.get('doctor_id')

    initial = {}
    if patient_id:
        initial['patient'] = get_object_or_404(Patient, pk=patient_id)
    if hospital_id:
        initial['hospital'] = get_object_or_404(Hospital, pk=hospital_id)
    if doctor_id:
        initial['doctor'] = get_object_or_404(User, pk=doctor_id, role='doctor')

    if request.method == 'POST':
        form = AppointmentBookingForm(request.POST, user=request.user)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.booked_by = request.user
            # If booked by health worker, default to confirmed or pending depending on facility
            appointment.status = 'confirmed'  # Direct confirmed token booking for rural health workers
            appointment.save()
            messages.success(
                request,
                f"Appointment booked successfully! Token #{appointment.token_number} generated for {appointment.patient.full_name}."
            )
            return redirect('appointments:appointment_print', pk=appointment.pk)
    else:
        form = AppointmentBookingForm(initial=initial, user=request.user)

    context = {
        'form': form,
        'title': 'Book OPD Appointment / नया ओपीडी अपॉइंटमेंट',
    }
    return render(request, 'appointments/appointment_form.html', context)


@login_required
def appointment_detail(request, pk):
    """View appointment record, clinical diagnosis, and action history"""
    appointment = get_object_or_404(
        Appointment.objects.select_related('patient', 'doctor__doctor_profile__specialty', 'hospital', 'booked_by'),
        pk=pk
    )
    qr_code_base64 = appointment.generate_qr_code_base64()
    
    context = {
        'appointment': appointment,
        'qr_code_base64': qr_code_base64,
        'can_consult': request.user == appointment.doctor or request.user.is_admin_user,
        'can_reschedule': request.user == appointment.doctor or request.user == appointment.booked_by or request.user.is_admin_user,
    }
    return render(request, 'appointments/appointment_detail.html', context)


@login_required
def appointment_print(request, pk):
    """Printable official OPD token slip / pass with QR verification"""
    appointment = get_object_or_404(
        Appointment.objects.select_related('patient', 'doctor__doctor_profile__specialty', 'hospital', 'booked_by'),
        pk=pk
    )
    qr_code_base64 = appointment.generate_qr_code_base64()

    context = {
        'appointment': appointment,
        'qr_code_base64': qr_code_base64,
        'print_time': timezone.now(),
    }
    return render(request, 'appointments/appointment_slip.html', context)


@doctor_required
def appointment_status_update(request, pk, new_status):
    """Doctor accepts, rejects, or completes appointment"""
    appointment = get_object_or_404(Appointment, pk=pk)
    
    if not request.user.is_superuser and appointment.doctor != request.user:
        messages.error(request, "You are not authorized to update this appointment.")
        return redirect('accounts:doctor_dashboard')

    valid_transitions = ['confirmed', 'cancelled', 'completed']
    if new_status in valid_transitions:
        appointment.status = new_status
        appointment.save()
        messages.success(request, f"Appointment status updated to '{appointment.get_status_display()}'.")
    else:
        messages.error(request, "Invalid status change requested.")

    return redirect('appointments:appointment_detail', pk=appointment.pk)


@doctor_required
def appointment_consultation(request, pk):
    """Doctor completes consultation, writes diagnosis and prescription"""
    appointment = get_object_or_404(Appointment, pk=pk)

    if not request.user.is_superuser and appointment.doctor != request.user:
        messages.error(request, "You are not authorized to update this consultation.")
        return redirect('accounts:doctor_dashboard')

    if request.method == 'POST':
        form = AppointmentConsultationForm(request.POST, instance=appointment)
        if form.is_valid():
            appt = form.save(commit=False)
            appt.status = 'completed'
            appt.save()
            messages.success(request, f"Consultation completed and prescription saved for {appt.patient.full_name}.")
            return redirect('appointments:appointment_detail', pk=appt.pk)
    else:
        form = AppointmentConsultationForm(instance=appointment)

    context = {
        'form': form,
        'appointment': appointment,
    }
    return render(request, 'appointments/appointment_consultation.html', context)


@health_worker_or_doctor_required
def appointment_reschedule(request, pk):
    """Reschedule date and slot of appointment"""
    appointment = get_object_or_404(Appointment, pk=pk)

    if request.method == 'POST':
        form = AppointmentRescheduleForm(request.POST, instance=appointment)
        if form.is_valid():
            appt = form.save(commit=False)
            appt.status = 'rescheduled'
            appt.save()
            messages.success(request, f"Appointment rescheduled to {appt.appointment_date} ({appt.time_slot}).")
            return redirect('appointments:appointment_detail', pk=appt.pk)
    else:
        form = AppointmentRescheduleForm(instance=appointment)

    context = {
        'form': form,
        'appointment': appointment,
    }
    return render(request, 'appointments/appointment_reschedule.html', context)


def api_doctors_by_hospital(request, hospital_id):
    """Returns JSON list of active doctors affiliated with chosen hospital"""
    doctors = User.objects.filter(
        role='doctor',
        doctor_profile__hospital_id=hospital_id,
        doctor_profile__is_available=True
    ).select_related('doctor_profile__specialty')

    data = []
    for d in doctors:
        doc_profile = getattr(d, 'doctor_profile', None)
        spec_name = doc_profile.specialty.name if doc_profile and doc_profile.specialty else "General Medicine"
        room = doc_profile.room_number if doc_profile else "OPD"
        data.append({
            'id': d.id,
            'name': f"Dr. {d.get_full_name() or d.username} ({spec_name})",
            'specialty': spec_name,
            'room': room,
        })
    return JsonResponse({'status': 'success', 'doctors': data})


def api_available_slots(request):
    """Returns already booked slots for a doctor on a specific date"""
    doctor_id = request.GET.get('doctor_id')
    date_str = request.GET.get('date')

    if not doctor_id or not date_str:
        return JsonResponse({'status': 'error', 'message': 'Missing doctor_id or date'})

    booked_slots = list(
        Appointment.objects.filter(
            doctor_id=doctor_id,
            appointment_date=date_str
        ).exclude(status__in=['cancelled', 'rescheduled']).values_list('time_slot', flat=True)
    )

    return JsonResponse({'status': 'success', 'booked_slots': booked_slots})
