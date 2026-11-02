import uuid
from django.conf import settings
from django.db import models


class Referral(models.Model):
    URGENCY_CHOICES = [
        ('routine', 'Routine / सामान्य रेफरल'),
        ('urgent', 'Urgent / त्वरित रेफरल'),
        ('emergency', 'Emergency / आपातकालीन रेफरल'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending Review / समीक्षाधीन'),
        ('accepted', 'Accepted / स्वीकृत'),
        ('in_transit', 'In Transit / रास्ते में'),
        ('attended', 'Attended / उपचार जारी'),
        ('completed', 'Completed / रेफरल पूर्ण'),
        ('rejected', 'Rejected / अस्वीकृत'),
    ]

    TRANSPORT_CHOICES = [
        ('not_needed', 'Not Required / आवश्यक नहीं'),
        ('requested', 'Ambulance 108 Requested / एम्बुलेंस बुलाई गई'),
        ('dispatched', 'Ambulance Dispatched / रवाना हुई'),
        ('arrived', 'Patient Arrived at Facility / अस्पताल पहुंचा'),
    ]

    referral_code = models.CharField(
        max_length=30,
        unique=True,
        editable=False,
        help_text="Unique Inter-facility Referral Slip Code"
    )
    patient = models.ForeignKey(
        'patients.Patient',
        on_delete=models.CASCADE,
        related_name='referrals'
    )
    from_hospital = models.ForeignKey(
        'hospitals.Hospital',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='outgoing_referrals',
        help_text="Originating Health Centre / PHC"
    )
    to_hospital = models.ForeignKey(
        'hospitals.Hospital',
        on_delete=models.CASCADE,
        related_name='incoming_referrals',
        help_text="Destination Referral Centre (CHC / District Hospital / Medical College)"
    )
    target_specialty = models.ForeignKey(
        'hospitals.Specialty',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='referred_cases'
    )
    assigned_doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_referrals',
        limit_choices_to={'role': 'doctor'}
    )
    referral_reason = models.TextField(help_text="Primary clinical justification for higher centre referral")
    clinical_summary = models.TextField(
        help_text="Provisional diagnosis, vitals at referral, medication given, investigations attached"
    )
    urgency = models.CharField(max_length=20, choices=URGENCY_CHOICES, default='routine')
    
    transport_required = models.BooleanField(
        default=False,
        help_text="Requires Dial 108 Govt Emergency Medical Transport"
    )
    transport_status = models.CharField(
        max_length=20,
        choices=TRANSPORT_CHOICES,
        default='not_needed'
    )
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    hospital_remarks = models.TextField(blank=True, help_text="Notes from receiving specialist or medical officer")
    
    referred_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='initiated_referrals'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.referral_code:
            code = uuid.uuid4().hex[:6].upper()
            self.referral_code = f"REF-{code}"
        super().save(*args, **kwargs)

    @property
    def status_badge_class(self):
        mapping = {
            'pending': 'bg-warning text-dark',
            'accepted': 'bg-info text-dark',
            'in_transit': 'bg-primary text-white',
            'attended': 'bg-teal text-white',
            'completed': 'bg-success text-white',
            'rejected': 'bg-danger text-white',
        }
        return mapping.get(self.status, 'bg-secondary')

    @property
    def urgency_badge_class(self):
        mapping = {
            'routine': 'badge-soft-success',
            'urgent': 'badge-soft-warning',
            'emergency': 'badge-soft-danger',
        }
        return mapping.get(self.urgency, 'badge-soft-secondary')

    def __str__(self):
        from_name = self.from_hospital.name if self.from_hospital else "Field / Community"
        return f"{self.referral_code}: {self.patient.full_name} ({from_name} ➔ {self.to_hospital.name})"
