from django import forms
from .models import Hospital, Specialty


class HospitalForm(forms.ModelForm):
    class Meta:
        model = Hospital
        fields = [
            'name', 'name_hi', 'facility_type', 'registration_number',
            'address', 'village_town', 'block', 'district', 'state', 'pincode',
            'latitude', 'longitude', 'contact_phone', 'emergency_phone',
            'ambulance_available', 'emergency_24x7', 'oxygen_plant_available',
            'blood_bank_available', 'total_beds', 'available_beds', 'icu_beds',
            'is_verified', 'specialties'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'name_hi': forms.TextInput(attrs={'class': 'form-control'}),
            'facility_type': forms.Select(attrs={'class': 'form-select'}),
            'registration_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'village_town': forms.TextInput(attrs={'class': 'form-control'}),
            'block': forms.TextInput(attrs={'class': 'form-control'}),
            'district': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'pincode': forms.TextInput(attrs={'class': 'form-control'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001'}),
            'contact_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'ambulance_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'emergency_24x7': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'oxygen_plant_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'blood_bank_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'total_beds': forms.NumberInput(attrs={'class': 'form-control'}),
            'available_beds': forms.NumberInput(attrs={'class': 'form-control'}),
            'icu_beds': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_verified': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'specialties': forms.SelectMultiple(attrs={'class': 'form-select', 'size': '6'}),
        }


class HospitalServiceUpdateForm(forms.ModelForm):
    class Meta:
        model = Hospital
        fields = [
            'total_beds', 'available_beds', 'icu_beds',
            'ambulance_available', 'emergency_24x7',
            'oxygen_plant_available', 'blood_bank_available'
        ]
        widgets = {
            'total_beds': forms.NumberInput(attrs={'class': 'form-control'}),
            'available_beds': forms.NumberInput(attrs={'class': 'form-control'}),
            'icu_beds': forms.NumberInput(attrs={'class': 'form-control'}),
            'ambulance_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'emergency_24x7': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'oxygen_plant_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'blood_bank_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
