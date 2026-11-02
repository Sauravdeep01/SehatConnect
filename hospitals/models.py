from django.db import models


class Specialty(models.Model):
    name = models.CharField(max_length=100, unique=True)
    name_hi = models.CharField(max_length=100, blank=True)
    code = models.CharField(max_length=30, blank=True)
    icon = models.CharField(max_length=50, default='bi-heart-pulse', help_text="Bootstrap icon name")
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Specialties"
        ordering = ['name']

    def __str__(self):
        if self.name_hi:
            return f"{self.name} ({self.name_hi})"
        return self.name


class Hospital(models.Model):
    FACILITY_TYPES = [
        ('sub_centre', 'Health Sub-Centre (HSC) / उप-स्वास्थ्य केंद्र'),
        ('phc', 'Primary Health Centre (PHC) / प्राथमिक स्वास्थ्य केंद्र'),
        ('chc', 'Community Health Centre (CHC) / सामुदायिक स्वास्थ्य केंद्र'),
        ('sdh', 'Sub-District Hospital (SDH) / उप-जिला अस्पताल'),
        ('dh', 'District Hospital (DH) / जिला अस्पताल'),
        ('mc', 'Government Medical College Hospital / मेडिकल कॉलेज'),
    ]

    name = models.CharField(max_length=200)
    name_hi = models.CharField(max_length=200, blank=True)
    facility_type = models.CharField(max_length=20, choices=FACILITY_TYPES, default='phc')
    registration_number = models.CharField(max_length=50, unique=True, help_text="State Health Dept Registry ID")
    address = models.TextField()
    village_town = models.CharField(max_length=100)
    block = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    state = models.CharField(max_length=100, default='Madhya Pradesh')
    pincode = models.CharField(max_length=10)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, default=23.259933)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, default=77.412615)
    contact_phone = models.CharField(max_length=20)
    emergency_phone = models.CharField(max_length=20, default='108')
    ambulance_available = models.BooleanField(default=True)
    emergency_24x7 = models.BooleanField(default=True)
    oxygen_plant_available = models.BooleanField(default=True)
    blood_bank_available = models.BooleanField(default=False)
    total_beds = models.PositiveIntegerField(default=30)
    available_beds = models.PositiveIntegerField(default=12)
    icu_beds = models.PositiveIntegerField(default=4)
    is_verified = models.BooleanField(default=True, help_text="Verified by District Health Administration")
    specialties = models.ManyToManyField(Specialty, blank=True, related_name='hospitals')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['district', 'name']

    @property
    def display_type(self):
        for code, label in self.FACILITY_TYPES:
            if code == self.facility_type:
                return label.split(' / ')[0]
        return self.facility_type.upper()

    @property
    def display_type_hi(self):
        for code, label in self.FACILITY_TYPES:
            if code == self.facility_type:
                parts = label.split(' / ')
                return parts[-1] if len(parts) > 1 else parts[0]
        return self.facility_type

    @property
    def occupancy_rate(self):
        if self.total_beds > 0:
            occupied = max(0, self.total_beds - self.available_beds)
            return round((occupied / self.total_beds) * 100, 1)
        return 0

    @property
    def badge_class(self):
        type_map = {
            'sub_centre': 'bg-secondary',
            'phc': 'bg-info text-dark',
            'chc': 'bg-primary',
            'sdh': 'bg-teal text-white',
            'dh': 'bg-success',
            'mc': 'bg-danger'
        }
        return type_map.get(self.facility_type, 'bg-primary')

    def __str__(self):
        return f"{self.name} [{self.get_facility_type_display().split(' / ')[0]}] - {self.block}, {self.district}"
