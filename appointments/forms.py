from django import forms
from django.utils import timezone
from .models import Appointment
from accounts.models import User
from hospitals.models import Hospital
from patients.models import Patient


class AppointmentBookingForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['patient', 'hospital', 'doctor', 'appointment_date', 'time_slot', 'urgency', 'symptoms']
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-select', 'id': 'id_patient'}),
            'hospital': forms.Select(attrs={'class': 'form-select', 'id': 'id_hospital'}),
            'doctor': forms.Select(attrs={'class': 'form-select', 'id': 'id_doctor'}),
            'appointment_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'id': 'id_appointment_date'
            }),
            'time_slot': forms.Select(attrs={'class': 'form-select', 'id': 'id_time_slot'}),
            'urgency': forms.Select(attrs={'class': 'form-select'}),
            'symptoms': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe symptoms, duration, and patient condition...'
            }),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # If user is a health worker, prioritize or limit patient choices to their village/managed patients
        if user and user.role == 'health_worker':
            self.fields['patient'].queryset = Patient.objects.all().order_by('-created_at')
        
        # Doctors queryset: only active doctors
        self.fields['doctor'].queryset = User.objects.filter(
            role='doctor',
            is_active=True,
            doctor_profile__is_available=True
        ).select_related('doctor_profile')
        
        # Set minimum date to today
        self.fields['appointment_date'].widget.attrs['min'] = timezone.now().date().isoformat()

    def clean(self):
        cleaned_data = super().clean()
        doctor = cleaned_data.get('doctor')
        patient = cleaned_data.get('patient')
        appointment_date = cleaned_data.get('appointment_date')
        time_slot = cleaned_data.get('time_slot')

        if appointment_date and appointment_date < timezone.now().date():
            self.add_error('appointment_date', "Appointment date cannot be in the past.")

        if doctor and appointment_date and time_slot:
            # Check for duplicate doctor slot
            existing_slot = Appointment.objects.filter(
                doctor=doctor,
                appointment_date=appointment_date,
                time_slot=time_slot
            ).exclude(status__in=['cancelled', 'rescheduled'])
            
            if self.instance.pk:
                existing_slot = existing_slot.exclude(pk=self.instance.pk)
                
            if existing_slot.exists():
                self.add_error('time_slot', f"This slot ({time_slot}) is already booked for this doctor. Please pick another slot.")

        if patient and doctor and appointment_date:
            # Check duplicate appointment for patient on same day
            existing_appt = Appointment.objects.filter(
                patient=patient,
                doctor=doctor,
                appointment_date=appointment_date
            ).exclude(status='cancelled')
            
            if self.instance.pk:
                existing_appt = existing_appt.exclude(pk=self.instance.pk)
                
            if existing_appt.exists():
                self.add_error('patient', f"Patient {patient.full_name} already has an active appointment with this doctor on {appointment_date}.")

        return cleaned_data


class AppointmentConsultationForm(forms.ModelForm):
    """Form used by Doctor during/after OPD consultation"""
    class Meta:
        model = Appointment
        fields = ['doctor_notes', 'prescription', 'follow_up_date']
        widgets = {
            'doctor_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter diagnosis, clinical observations, vitals review, lab tests ordered...'
            }),
            'prescription': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Medicine Name, Dosage (e.g. Paracetamol 500mg 1-0-1 for 3 days), Dietary advice...'
            }),
            'follow_up_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }


class AppointmentRescheduleForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['appointment_date', 'time_slot']
        widgets = {
            'appointment_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'time_slot': forms.Select(attrs={'class': 'form-select'}),
        }
