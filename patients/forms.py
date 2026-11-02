from django import forms
from .models import Patient, PatientVital


class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = [
            'full_name', 'age', 'gender', 'guardian_name', 'phone', 'abha_id',
            'village', 'panchayat', 'block', 'district', 'state', 'pincode',
            'blood_group', 'allergies', 'chronic_conditions',
            'emergency_contact_name', 'emergency_contact_phone', 'consent_given'
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Ramesh Chandra Verma'}),
            'age': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Years'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'guardian_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Father or Husband name'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '10-digit mobile number'}),
            'abha_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional 14-digit ABHA ID'}),
            'village': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Village name'}),
            'panchayat': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Gram Panchayat'}),
            'block': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Block / Tehsil'}),
            'district': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'District'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'pincode': forms.TextInput(attrs={'class': 'form-control'}),
            'blood_group': forms.Select(attrs={'class': 'form-select'}),
            'allergies': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Penicillin, dust, etc.'}),
            'chronic_conditions': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Hypertension, Diabetes, Asthma, Sickle Cell...'}),
            'emergency_contact_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contact person'}),
            'emergency_contact_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Emergency phone number'}),
            'consent_given': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class PatientVitalForm(forms.ModelForm):
    class Meta:
        model = PatientVital
        fields = [
            'blood_pressure_systolic', 'blood_pressure_diastolic',
            'pulse_rate', 'body_temperature', 'spo2', 'blood_sugar',
            'weight_kg', 'height_cm', 'notes'
        ]
        widgets = {
            'blood_pressure_systolic': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 120'}),
            'blood_pressure_diastolic': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 80'}),
            'pulse_rate': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'BPM'}),
            'body_temperature': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': '°F'}),
            'spo2': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '%'}),
            'blood_sugar': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'mg/dL'}),
            'weight_kg': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': 'kg'}),
            'height_cm': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': 'cm'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Clinical observations by ASHA...'}),
        }
