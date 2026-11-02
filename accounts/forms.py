from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm
from .models import User, HealthWorkerProfile, DoctorProfile
from hospitals.models import Hospital, Specialty


class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Enter Username or Employee ID / यूजरनेम दर्ज करें',
            'autofocus': True,
        }),
        label="Username / यूजरनेम"
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Enter Password / पासवर्ड दर्ज करें',
        }),
        label="Password / पासवर्ड"
    )

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise forms.ValidationError("Invalid credentials. Please verify your username and password.")
            if not user.is_active:
                raise forms.ValidationError("This account is currently inactive. Contact your District Administrator.")
            cleaned_data['user'] = user
        return cleaned_data


class UserProfileUpdateForm(forms.ModelForm):
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="First Name / पहला नाम"
    )
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Last Name / अंतिम नाम"
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        required=False,
        label="Email Address / ईमेल"
    )
    phone_number = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Contact Phone / मोबाइल नंबर"
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number']


class HealthWorkerProfileForm(forms.ModelForm):
    class Meta:
        model = HealthWorkerProfile
        fields = ['assigned_village', 'panchayat', 'block', 'district', 'state', 'qualification', 'experience_years', 'asha_badge_number']
        widgets = {
            'assigned_village': forms.TextInput(attrs={'class': 'form-control'}),
            'panchayat': forms.TextInput(attrs={'class': 'form-control'}),
            'block': forms.TextInput(attrs={'class': 'form-control'}),
            'district': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'qualification': forms.TextInput(attrs={'class': 'form-control'}),
            'experience_years': forms.NumberInput(attrs={'class': 'form-control'}),
            'asha_badge_number': forms.TextInput(attrs={'class': 'form-control'}),
        }


class DoctorProfileForm(forms.ModelForm):
    class Meta:
        model = DoctorProfile
        fields = ['hospital', 'specialty', 'license_number', 'qualification', 'opd_days', 'opd_start_time', 'opd_end_time', 'max_daily_patients', 'room_number', 'is_available']
        widgets = {
            'hospital': forms.Select(attrs={'class': 'form-select'}),
            'specialty': forms.Select(attrs={'class': 'form-select'}),
            'license_number': forms.TextInput(attrs={'class': 'form-control'}),
            'qualification': forms.TextInput(attrs={'class': 'form-control'}),
            'opd_days': forms.TextInput(attrs={'class': 'form-control'}),
            'opd_start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'opd_end_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'max_daily_patients': forms.NumberInput(attrs={'class': 'form-control'}),
            'room_number': forms.TextInput(attrs={'class': 'form-control'}),
            'is_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
