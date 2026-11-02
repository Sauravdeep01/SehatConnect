from django import forms
from .models import Referral
from hospitals.models import Hospital, Specialty
from patients.models import Patient


class ReferralCreateForm(forms.ModelForm):
    class Meta:
        model = Referral
        fields = [
            'patient', 'from_hospital', 'to_hospital', 'target_specialty',
            'referral_reason', 'clinical_summary', 'urgency', 'transport_required'
        ]
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-select'}),
            'from_hospital': forms.Select(attrs={'class': 'form-select'}),
            'to_hospital': forms.Select(attrs={'class': 'form-select'}),
            'target_specialty': forms.Select(attrs={'class': 'form-select'}),
            'referral_reason': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Reason for higher centre escalation (e.g. Obstructed labor, Cardiac pain, Complex fracture)...'
            }),
            'clinical_summary': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Provisional diagnosis, current vitals (BP, SpO2, Pulse), medications already administered...'
            }),
            'urgency': forms.Select(attrs={'class': 'form-select'}),
            'transport_required': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ReferralStatusUpdateForm(forms.ModelForm):
    class Meta:
        model = Referral
        fields = ['status', 'transport_status', 'hospital_remarks']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'transport_status': forms.Select(attrs={'class': 'form-select'}),
            'hospital_remarks': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Receiving remarks, bed allocated, ICU admission details...'
            }),
        }
