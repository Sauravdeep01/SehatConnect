from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_HEALTH_WORKER = 'health_worker'
    ROLE_DOCTOR = 'doctor'
    ROLE_ADMIN = 'admin'

    ROLE_CHOICES = [
        (ROLE_HEALTH_WORKER, 'Health Worker / ASHA Worker / आशा कार्यकर्ता'),
        (ROLE_DOCTOR, 'Doctor / Hospital Staff / चिकित्सक'),
        (ROLE_ADMIN, 'Administrator / प्रशासक'),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=ROLE_HEALTH_WORKER,
        help_text="Designated user role within the rural healthcare system"
    )
    phone_number = models.CharField(max_length=15, blank=True, help_text="10-digit mobile number")
    employee_id = models.CharField(max_length=30, blank=True, null=True, unique=True, help_text="Govt / System ID")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def is_health_worker(self):
        return self.role == self.ROLE_HEALTH_WORKER

    @property
    def is_doctor_user(self):
        return self.role == self.ROLE_DOCTOR

    @property
    def is_admin_user(self):
        return self.role == self.ROLE_ADMIN or self.is_superuser

    @property
    def display_role_name(self):
        for code, label in self.ROLE_CHOICES:
            if code == self.role:
                return label.split(' / ')[0]
        return self.role.title()

    @property
    def display_role_hindi(self):
        for code, label in self.ROLE_CHOICES:
            if code == self.role:
                parts = label.split(' / ')
                return parts[-1] if len(parts) > 1 else parts[0]
        return self.role

    def __str__(self):
        full_name = self.get_full_name()
        if full_name:
            return f"{full_name} ({self.get_role_display()})"
        return f"{self.username} ({self.get_role_display()})"


class HealthWorkerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='health_worker_profile')
    assigned_village = models.CharField(max_length=100, help_text="Primary Village served")
    panchayat = models.CharField(max_length=100, blank=True, help_text="Gram Panchayat")
    block = models.CharField(max_length=100, help_text="Administrative Tehsil / Block")
    district = models.CharField(max_length=100, help_text="District name")
    state = models.CharField(max_length=100, default='Madhya Pradesh')
    qualification = models.CharField(max_length=150, default='ASHA / ANM / MPW Certified')
    experience_years = models.PositiveIntegerField(default=3)
    asha_badge_number = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"ASHA: {self.user.get_full_name() or self.user.username} - {self.assigned_village}, {self.block}"


class DoctorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile')
    hospital = models.ForeignKey('hospitals.Hospital', on_delete=models.SET_NULL, null=True, blank=True, related_name='doctors')
    specialty = models.ForeignKey('hospitals.Specialty', on_delete=models.SET_NULL, null=True, blank=True, related_name='doctors')
    license_number = models.CharField(max_length=50, help_text="State Medical Council Registration No.")
    qualification = models.CharField(max_length=150, default='MBBS')
    opd_days = models.CharField(max_length=150, default='Mon, Tue, Wed, Thu, Fri, Sat', help_text="OPD schedule days")
    opd_start_time = models.TimeField(default='09:00:00')
    opd_end_time = models.TimeField(default='14:00:00')
    max_daily_patients = models.PositiveIntegerField(default=35, help_text="Daily OPD token limit")
    room_number = models.CharField(max_length=50, default='OPD Room 1')
    is_available = models.BooleanField(default=True, help_text="Active for new patient appointments")

    def __str__(self):
        hosp_name = self.hospital.name if self.hospital else "Unassigned Hospital"
        return f"Dr. {self.user.get_full_name() or self.user.username} ({self.specialty.name if self.specialty else 'General'}) - {hosp_name}"
