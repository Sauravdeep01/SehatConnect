from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from .forms import HospitalForm, HospitalServiceUpdateForm
from .models import Hospital, Specialty
from accounts.decorators import doctor_required, admin_required


def hospital_list(request):
    """Search and browse verified healthcare facilities across blocks & districts"""
    query = request.GET.get('q', '').strip()
    district = request.GET.get('district', '').strip()
    facility_type = request.GET.get('facility_type', '')
    specialty_id = request.GET.get('specialty', '')
    ambulance = request.GET.get('ambulance') == '1'
    emergency = request.GET.get('emergency') == '1'

    hospitals = Hospital.objects.filter(is_verified=True).prefetch_related('specialties', 'doctors')

    if query:
        hospitals = hospitals.filter(
            Q(name__icontains=query) |
            Q(name_hi__icontains=query) |
            Q(village_town__icontains=query) |
            Q(block__icontains=query) |
            Q(district__icontains=query)
        )

    if district:
        hospitals = hospitals.filter(district__iexact=district)

    if facility_type:
        hospitals = hospitals.filter(facility_type=facility_type)

    if specialty_id:
        hospitals = hospitals.filter(specialties__id=specialty_id)

    if ambulance:
        hospitals = hospitals.filter(ambulance_available=True)

    if emergency:
        hospitals = hospitals.filter(emergency_24x7=True)

    # Distict list for filter dropdown
    districts = Hospital.objects.filter(is_verified=True).values_list('district', flat=True).distinct()
    specialties = Specialty.objects.all()

    paginator = Paginator(hospitals, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'query': query,
        'district': district,
        'facility_type': facility_type,
        'specialty_id': specialty_id,
        'ambulance': ambulance,
        'emergency': emergency,
        'districts': sorted(list(set(districts))),
        'specialties': specialties,
        'facility_types': Hospital.FACILITY_TYPES,
        'total_count': hospitals.count(),
    }
    return render(request, 'hospitals/hospital_list.html', context)


def hospital_map(request):
    """Dedicated interactive Leaflet OpenStreetMap view"""
    specialties = Specialty.objects.all()
    facility_types = Hospital.FACILITY_TYPES
    districts = Hospital.objects.filter(is_verified=True).values_list('district', flat=True).distinct()

    context = {
        'specialties': specialties,
        'facility_types': facility_types,
        'districts': sorted(list(set(districts))),
    }
    return render(request, 'hospitals/hospital_map.html', context)


def hospital_detail(request, pk):
    """Detailed view of a hospital including doctors, beds, and services"""
    hospital = get_object_or_404(Hospital.objects.prefetch_related('specialties', 'doctors__user', 'doctors__specialty'), pk=pk)
    doctors = hospital.doctors.filter(is_available=True)
    
    context = {
        'hospital': hospital,
        'doctors': doctors,
    }
    return render(request, 'hospitals/hospital_detail.html', context)


@doctor_required
def hospital_services_update(request, pk):
    """Doctor or hospital staff updates bed availability and emergency readiness"""
    hospital = get_object_or_404(Hospital, pk=pk)
    
    # Check if doctor belongs to this hospital or is superuser
    if not request.user.is_superuser:
        doctor_profile = getattr(request.user, 'doctor_profile', None)
        if not doctor_profile or doctor_profile.hospital_id != hospital.id:
            messages.error(request, "You are only authorized to update your assigned hospital.")
            return redirect('accounts:doctor_dashboard')

    if request.method == 'POST':
        form = HospitalServiceUpdateForm(request.POST, instance=hospital)
        if form.is_valid():
            form.save()
            messages.success(request, f"Updated services and bed capacity for {hospital.name}.")
            return redirect('hospitals:hospital_detail', pk=hospital.pk)
    else:
        form = HospitalServiceUpdateForm(instance=hospital)

    context = {
        'form': form,
        'hospital': hospital,
    }
    return render(request, 'hospitals/hospital_service_form.html', context)


def api_hospitals_json(request):
    """JSON API endpoint supplying geolocation markers for Leaflet map"""
    district = request.GET.get('district', '')
    facility_type = request.GET.get('facility_type', '')
    specialty_id = request.GET.get('specialty', '')
    
    hospitals = Hospital.objects.filter(is_verified=True).prefetch_related('specialties')
    
    if district:
        hospitals = hospitals.filter(district__iexact=district)
    if facility_type:
        hospitals = hospitals.filter(facility_type=facility_type)
    if specialty_id:
        hospitals = hospitals.filter(specialties__id=specialty_id)
        
    data = []
    for h in hospitals:
        data.append({
            'id': h.id,
            'name': h.name,
            'name_hi': h.name_hi or h.name,
            'facility_type': h.facility_type,
            'facility_type_display': h.display_type,
            'lat': float(h.latitude),
            'lng': float(h.longitude),
            'district': h.district,
            'block': h.block,
            'village_town': h.village_town,
            'phone': h.contact_phone,
            'emergency_phone': h.emergency_phone,
            'total_beds': h.total_beds,
            'available_beds': h.available_beds,
            'icu_beds': h.icu_beds,
            'ambulance': h.ambulance_available,
            'emergency_24x7': h.emergency_24x7,
            'specialties': [s.name for s in h.specialties.all()[:3]],
            'url': f"/hospitals/{h.id}/",
        })
        
    return JsonResponse({'status': 'success', 'count': len(data), 'hospitals': data})


@admin_required
def admin_hospital_create(request):
    """Admin registers a new hospital facility"""
    if request.method == 'POST':
        form = HospitalForm(request.POST)
        if form.is_valid():
            hospital = form.save()
            messages.success(request, f"Hospital '{hospital.name}' added successfully.")
            return redirect('hospitals:hospital_detail', pk=hospital.pk)
    else:
        form = HospitalForm()

    return render(request, 'hospitals/hospital_form.html', {'form': form, 'title': 'Register New Hospital / नया अस्पताल पंजीयन'})


@admin_required
def admin_hospital_edit(request, pk):
    """Admin edits hospital facility"""
    hospital = get_object_or_404(Hospital, pk=pk)
    if request.method == 'POST':
        form = HospitalForm(request.POST, instance=hospital)
        if form.is_valid():
            form.save()
            messages.success(request, f"Hospital '{hospital.name}' updated successfully.")
            return redirect('hospitals:hospital_detail', pk=hospital.pk)
    else:
        form = HospitalForm(instance=hospital)

    return render(request, 'hospitals/hospital_form.html', {'form': form, 'hospital': hospital, 'title': f'Edit Hospital: {hospital.name}'})
