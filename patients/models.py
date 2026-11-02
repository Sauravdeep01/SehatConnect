import uuid
from django.conf import settings
from django.db import models


class Patient(models.Model):
    GENDER_CHOICES = [
        ('male', 'Male / पुरुष'),
        ('female', 'Female / महिला'),
        ('other', 'Other / अन्य'),
    ]

    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
        ('unknown', 'Unknown / अज्ञात'),
    ]

    registration_id = models.CharField(
        max_length=30,
        unique=True,
        editable=False,
        help_text="Unique Rural Patient Identification Code"
    )
    abha_id = models.CharField(
        max_length=25,
        blank=True,
        null=True,
        help_text="Ayushman Bharat Health Account (ABHA ID)"
    )
    full_name = models.CharField(max_length=150, help_text="Full Patient Name")
    age = models.PositiveIntegerField(help_text="Age in years")
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='female')
    guardian_name = models.CharField(max_length=150, blank=True, help_text="Father / Husband / Guardian Name")
    phone = models.CharField(max_length=15, blank=True, help_text="Patient or family contact phone")
    
    # Rural Address Details
    village = models.CharField(max_length=100, help_text="Village name (गांव)")
    panchayat = models.CharField(max_length=100, blank=True, help_text="Gram Panchayat")
    block = models.CharField(max_length=100, help_text="Block / Tehsil (तहसील/ब्लॉक)")
    district = models.CharField(max_length=100, help_text="District (जिला)")
    state = models.CharField(max_length=100, default='Madhya Pradesh')
    pincode = models.CharField(max_length=10, blank=True)

    # Health & Medical Background
    blood_group = models.CharField(max_length=10, choices=BLOOD_GROUP_CHOICES, default='unknown')
    allergies = models.TextField(blank=True, help_text="Known drug/food allergies")
    chronic_conditions = models.TextField(
        blank=True,
        help_text="e.g. Hypertension, Diabetes, Asthma, Tuberculosis, Sickle Cell Anemia"
    )
    
    # Emergency and Consent
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=15, blank=True)
    consent_given = models.BooleanField(
        default=True,
        help_text="Informed consent obtained by community health worker on behalf of patient"
    )

    # Worker Assignment & Timestamps
    registered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='registered_patients'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.registration_id:
            # Generate deterministic rural health identifier e.g. SC-2026-A1B2
            token = uuid.uuid4().hex[:6].upper()
            self.registration_id = f"SC-PAT-{token}"
        super().save(*args, **kwargs)

    @property
    def latest_vitals(self):
        return self.vitals.order_by('-recorded_at').first()

    @property
    def gender_display(self):
        for code, label in self.GENDER_CHOICES:
            if code == self.gender:
                return label.split(' / ')[0]
        return self.gender.title()

    @property
    def full_address(self):
        parts = [self.village]
        if self.panchayat:
            parts.append(f"GP: {self.panchayat}")
        parts.extend([self.block, self.district, self.state])
        return ", ".join(parts)

    def __str__(self):
        return f"{self.full_name} ({self.registration_id}) - {self.village}, {self.block}"


class PatientVital(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='vitals')
    blood_pressure_systolic = models.PositiveIntegerField(null=True, blank=True, help_text="mmHg (e.g. 120)")
    blood_pressure_diastolic = models.PositiveIntegerField(null=True, blank=True, help_text="mmHg (e.g. 80)")
    pulse_rate = models.PositiveIntegerField(null=True, blank=True, help_text="Beats per min (e.g. 74)")
    body_temperature = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True, help_text="°F (e.g. 98.6)")
    spo2 = models.PositiveIntegerField(null=True, blank=True, help_text="Blood Oxygen Saturation % (e.g. 98)")
    blood_sugar = models.PositiveIntegerField(null=True, blank=True, help_text="mg/dL (e.g. 110)")
    weight_kg = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="kg")
    height_cm = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="cm")
    notes = models.TextField(blank=True, help_text="Observation notes by ASHA / ANM")
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-recorded_at']

    @property
    def bp_display(self):
        if self.blood_pressure_systolic and self.blood_pressure_diastolic:
            return f"{self.blood_pressure_systolic}/{self.blood_pressure_diastolic} mmHg"
        return "N/A"

    @property
    def bmi(self):
        if self.weight_kg and self.height_cm and self.height_cm > 0:
            height_m = float(self.height_cm) / 100.0
            return round(float(self.weight_kg) / (height_m * height_m), 1)
        return None

    def __str__(self):
        return f"Vitals for {self.patient.full_name} on {self.recorded_at.strftime('%Y-%m-%d %H:%M')}"
