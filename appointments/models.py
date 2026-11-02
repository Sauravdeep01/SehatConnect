import base64
import io
import uuid
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Appointment(models.Model):
    URGENCY_CHOICES = [
        ('normal', 'Normal / सामान्य'),
        ('urgent', 'Urgent / गंभीर'),
        ('emergency', 'Emergency / आपातकालीन'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending / लंबित'),
        ('confirmed', 'Confirmed / स्वीकृत'),
        ('rescheduled', 'Rescheduled / पुनर्निर्धारित'),
        ('completed', 'Completed / पूर्ण'),
        ('cancelled', 'Cancelled / रद्द'),
    ]

    TIME_SLOTS = [
        ('09:00 AM - 09:30 AM', '09:00 AM - 09:30 AM'),
        ('09:30 AM - 10:00 AM', '09:30 AM - 10:00 AM'),
        ('10:00 AM - 10:30 AM', '10:00 AM - 10:30 AM'),
        ('10:30 AM - 11:00 AM', '10:30 AM - 11:00 AM'),
        ('11:00 AM - 11:30 AM', '11:00 AM - 11:30 AM'),
        ('11:30 AM - 12:00 PM', '11:30 AM - 12:00 PM'),
        ('12:00 PM - 12:30 PM', '12:00 PM - 12:30 PM'),
        ('12:30 PM - 01:00 PM', '12:30 PM - 01:00 PM'),
        ('02:00 PM - 02:30 PM', '02:00 PM - 02:30 PM'),
        ('02:30 PM - 03:00 PM', '02:30 PM - 03:00 PM'),
        ('03:00 PM - 03:30 PM', '03:00 PM - 03:30 PM'),
        ('03:30 PM - 04:00 PM', '03:30 PM - 04:00 PM'),
    ]

    appointment_number = models.CharField(
        max_length=30,
        unique=True,
        editable=False,
        help_text="Official Appointment Token Slip Identifier"
    )
    patient = models.ForeignKey(
        'patients.Patient',
        on_delete=models.CASCADE,
        related_name='appointments'
    )
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='doctor_appointments',
        limit_choices_to={'role': 'doctor'}
    )
    hospital = models.ForeignKey(
        'hospitals.Hospital',
        on_delete=models.CASCADE,
        related_name='appointments'
    )
    appointment_date = models.DateField(help_text="OPD Consultation Date")
    time_slot = models.CharField(max_length=30, choices=TIME_SLOTS, default='09:00 AM - 09:30 AM')
    token_number = models.PositiveIntegerField(help_text="OPD Queue Token Number")
    
    urgency = models.CharField(max_length=20, choices=URGENCY_CHOICES, default='normal')
    symptoms = models.TextField(help_text="Chief complaints / symptoms described by patient")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    booked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='booked_appointments'
    )
    
    # Clinical Outcomes
    doctor_notes = models.TextField(blank=True, verbose_name="Diagnosis / Clinical Observations")
    prescription = models.TextField(blank=True, verbose_name="Prescribed Medicines & Dosages")
    follow_up_date = models.DateField(null=True, blank=True, verbose_name="Follow-up Date")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-appointment_date', 'token_number']

    def clean(self):
        super().clean()
        if self.appointment_date and self.appointment_date < timezone.now().date() and not self.pk:
            raise ValidationError("Appointment date cannot be in the past.")

        # Check for duplicate appointment by same patient with same doctor on same date
        active_patient_appts = Appointment.objects.filter(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=self.appointment_date
        ).exclude(status='cancelled')
        if self.pk:
            active_patient_appts = active_patient_appts.exclude(pk=self.pk)
        if active_patient_appts.exists():
            raise ValidationError(
                f"Patient {self.patient.full_name} already has an active appointment with this doctor on {self.appointment_date}."
            )

        # Check for slot collision: Doctor cannot be double-booked for the same date and slot
        active_doctor_slots = Appointment.objects.filter(
            doctor=self.doctor,
            appointment_date=self.appointment_date,
            time_slot=self.time_slot
        ).exclude(status__in=['cancelled', 'rescheduled'])
        if self.pk:
            active_doctor_slots = active_doctor_slots.exclude(pk=self.pk)
        if active_doctor_slots.exists():
            raise ValidationError(
                f"Time slot '{self.time_slot}' on {self.appointment_date} is already booked for this doctor. Please select another slot."
            )

    def save(self, *args, **kwargs):
        if not self.appointment_number:
            code = uuid.uuid4().hex[:6].upper()
            date_str = self.appointment_date.strftime('%Y%m%d') if self.appointment_date else timezone.now().strftime('%Y%m%d')
            self.appointment_number = f"APT-{date_str}-{code}"
        
        if not self.token_number and self.doctor and self.appointment_date:
            # Auto-assign next token for that doctor on that date
            last_token = Appointment.objects.filter(
                doctor=self.doctor,
                appointment_date=self.appointment_date
            ).aggregate(models.Max('token_number'))['token_number__max']
            self.token_number = (last_token or 0) + 1
        elif not self.token_number:
            self.token_number = 1

        super().save(*args, **kwargs)

    @property
    def is_upcoming(self):
        return self.appointment_date >= timezone.now().date() and self.status in ['pending', 'confirmed']

    @property
    def status_badge_class(self):
        mapping = {
            'pending': 'bg-warning text-dark',
            'confirmed': 'bg-success text-white',
            'rescheduled': 'bg-info text-dark',
            'completed': 'bg-primary text-white',
            'cancelled': 'bg-danger text-white',
        }
        return mapping.get(self.status, 'bg-secondary')

    @property
    def urgency_badge_class(self):
        mapping = {
            'normal': 'badge-soft-success',
            'urgent': 'badge-soft-warning',
            'emergency': 'badge-soft-danger',
        }
        return mapping.get(self.urgency, 'badge-soft-secondary')

    def generate_qr_code_base64(self):
        """Generates a QR code image as base64 string for printable OPD slip"""
        try:
            import qrcode
            qr_content = (
                f"SehatConnect OPD Slip\n"
                f"Token: #{self.token_number}\n"
                f"Slip No: {self.appointment_number}\n"
                f"Patient: {self.patient.full_name} ({self.patient.registration_id})\n"
                f"Doctor: Dr. {self.doctor.get_full_name() or self.doctor.username}\n"
                f"Hospital: {self.hospital.name}\n"
                f"Date: {self.appointment_date} | Slot: {self.time_slot}\n"
                f"Status: {self.get_status_display()}"
            )
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=6,
                border=2,
            )
            qr.add_data(qr_content)
            qr.make(fit=True)
            img = qr.make_image(fill_color="#0b5ed7", back_color="white")
            buffer = io.BytesIO()
            img.save(buffer, format="PNG")
            return base64.b64encode(buffer.getvalue()).decode()
        except Exception:
            return ""

    def __str__(self):
        return f"Token #{self.token_number} - {self.patient.full_name} with Dr. {self.doctor.get_full_name() or self.doctor.username} on {self.appointment_date}"
