import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.models import User, HealthWorkerProfile, DoctorProfile
from appointments.models import Appointment
from hospitals.models import Hospital, Specialty
from patients.models import Patient, PatientVital
from referrals.models import Referral


class Command(BaseCommand):
    help = "Seeds database with realistic rural healthcare demo data (Users, Hospitals, Doctors, Patients, Appointments, Referrals)"

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Initializing SehatConnect demo data seeding..."))

        # 1. Create Specialties
        specialties_data = [
            ("General Medicine", "सामान्य चिकित्सा", "bi-capsule", "Primary outpatient care and fever/infection management"),
            ("Pediatrics", "बाल रोग विशेषज्ञ", "bi-emoji-smile", "Infant and child growth, vaccination and pediatric disorders"),
            ("Obstetrics & Gynaecology", "प्रसूति एवं स्त्री रोग", "bi-gender-female", "Antenatal care, safe institutional deliveries and maternal health"),
            ("Orthopaedics", "हड्डी रोग विशेषज्ञ", "bi-bandaid", "Fracture care, bone trauma and joint pain"),
            ("Cardiology", "हृदय रोग विशेषज्ञ", "bi-heart-pulse", "Cardiovascular management, hypertension and ECG"),
            ("Ophthalmology", "नेत्र रोग विशेषज्ञ", "bi-eye", "Cataract screening, vision testing and eye care"),
            ("Emergency & Trauma", "आपातकालीन एवं ट्रॉमा", "bi-hospital", "24x7 emergency life support and acute stabilization"),
        ]

        specialty_objs = {}
        for name, name_hi, icon, desc in specialties_data:
            spec, _ = Specialty.objects.get_or_create(
                name=name,
                defaults={'name_hi': name_hi, 'icon': icon, 'description': desc}
            )
            specialty_objs[name] = spec

        self.stdout.write(self.style.SUCCESS(f"Loaded {len(specialty_objs)} medical specialties."))

        # 2. Create Hospitals (Central Madhya Pradesh coordinates)
        hospitals_data = [
            {
                'name': 'District Hospital Raisen (जिला अस्पताल रायसेन)',
                'name_hi': 'जिला अस्पताल रायसेन',
                'facility_type': 'dh',
                'registration_number': 'MP-RAISEN-DH-01',
                'address': 'Collectorate Road, Civil Lines, Raisen',
                'village_town': 'Raisen',
                'block': 'Raisen',
                'district': 'Raisen',
                'state': 'Madhya Pradesh',
                'pincode': '464551',
                'latitude': 23.332300,
                'longitude': 77.781800,
                'contact_phone': '07482-222108',
                'emergency_phone': '108',
                'ambulance_available': True,
                'emergency_24x7': True,
                'oxygen_plant_available': True,
                'blood_bank_available': True,
                'total_beds': 150,
                'available_beds': 42,
                'icu_beds': 12,
                'is_verified': True,
                'specs': ["General Medicine", "Pediatrics", "Obstetrics & Gynaecology", "Orthopaedics", "Cardiology", "Emergency & Trauma"],
            },
            {
                'name': 'Community Health Centre Sanchi (सामुदायिक स्वास्थ्य केंद्र सांची)',
                'name_hi': 'सामुदायिक स्वास्थ्य केंद्र सांची',
                'facility_type': 'chc',
                'registration_number': 'MP-RAISEN-CHC-02',
                'address': 'NH-86 Sanchi-Vidisha Highway, Sanchi',
                'village_town': 'Sanchi',
                'block': 'Sanchi',
                'district': 'Raisen',
                'state': 'Madhya Pradesh',
                'pincode': '464661',
                'latitude': 23.487300,
                'longitude': 77.741000,
                'contact_phone': '07482-266100',
                'emergency_phone': '108',
                'ambulance_available': True,
                'emergency_24x7': True,
                'oxygen_plant_available': True,
                'blood_bank_available': False,
                'total_beds': 30,
                'available_beds': 9,
                'icu_beds': 2,
                'is_verified': True,
                'specs': ["General Medicine", "Pediatrics", "Obstetrics & Gynaecology"],
            },
            {
                'name': 'Primary Health Centre Salamatpur (प्राथमिक स्वास्थ्य केंद्र सलामतपुर)',
                'name_hi': 'प्राथमिक स्वास्थ्य केंद्र सलामतपुर',
                'facility_type': 'phc',
                'registration_number': 'MP-RAISEN-PHC-07',
                'address': 'Main Market Road, Salamatpur',
                'village_town': 'Salamatpur',
                'block': 'Sanchi',
                'district': 'Raisen',
                'state': 'Madhya Pradesh',
                'pincode': '464662',
                'latitude': 23.424100,
                'longitude': 77.671200,
                'contact_phone': '07482-271010',
                'emergency_phone': '108',
                'ambulance_available': True,
                'emergency_24x7': False,
                'oxygen_plant_available': False,
                'blood_bank_available': False,
                'total_beds': 6,
                'available_beds': 4,
                'icu_beds': 0,
                'is_verified': True,
                'specs': ["General Medicine"],
            },
            {
                'name': 'Atal Bihari Vajpayee Govt Medical College Hospital Vidisha (मेडिकल कॉलेज विदिशा)',
                'name_hi': 'अटल बिहारी वाजपेयी मेडिकल कॉलेज अस्पताल विदिशा',
                'facility_type': 'mc',
                'registration_number': 'MP-VIDISHA-GMC-01',
                'address': 'Kharabai Road, Vidisha',
                'village_town': 'Vidisha',
                'block': 'Vidisha',
                'district': 'Vidisha',
                'state': 'Madhya Pradesh',
                'pincode': '464001',
                'latitude': 23.525100,
                'longitude': 77.810500,
                'contact_phone': '07592-250100',
                'emergency_phone': '108',
                'ambulance_available': True,
                'emergency_24x7': True,
                'oxygen_plant_available': True,
                'blood_bank_available': True,
                'total_beds': 500,
                'available_beds': 118,
                'icu_beds': 45,
                'is_verified': True,
                'specs': ["General Medicine", "Pediatrics", "Obstetrics & Gynaecology", "Orthopaedics", "Cardiology", "Ophthalmology", "Emergency & Trauma"],
            },
            {
                'name': 'District Hospital Sehore (जिला अस्पताल सीहोर)',
                'name_hi': 'जिला अस्पताल सीहोर',
                'facility_type': 'dh',
                'registration_number': 'MP-SEHORE-DH-01',
                'address': 'Bhopal-Indore Road, Sehore',
                'village_town': 'Sehore',
                'block': 'Sehore',
                'district': 'Sehore',
                'state': 'Madhya Pradesh',
                'pincode': '466001',
                'latitude': 23.203100,
                'longitude': 77.084400,
                'contact_phone': '07562-224400',
                'emergency_phone': '108',
                'ambulance_available': True,
                'emergency_24x7': True,
                'oxygen_plant_available': True,
                'blood_bank_available': True,
                'total_beds': 200,
                'available_beds': 55,
                'icu_beds': 16,
                'is_verified': True,
                'specs': ["General Medicine", "Pediatrics", "Obstetrics & Gynaecology", "Orthopaedics", "Emergency & Trauma"],
            },
            {
                'name': 'Community Health Centre Gairatganj (सामुदायिक स्वास्थ्य केंद्र गैरतगंज)',
                'name_hi': 'सामुदायिक स्वास्थ्य केंद्र गैरतगंज',
                'facility_type': 'chc',
                'registration_number': 'MP-RAISEN-CHC-05',
                'address': 'Gairatganj Main Road, Tehsil Headquarter',
                'village_town': 'Gairatganj',
                'block': 'Gairatganj',
                'district': 'Raisen',
                'state': 'Madhya Pradesh',
                'pincode': '464884',
                'latitude': 23.407200,
                'longitude': 78.238400,
                'contact_phone': '07484-252100',
                'emergency_phone': '108',
                'ambulance_available': True,
                'emergency_24x7': True,
                'oxygen_plant_available': True,
                'blood_bank_available': False,
                'total_beds': 30,
                'available_beds': 14,
                'icu_beds': 2,
                'is_verified': True,
                'specs': ["General Medicine", "Obstetrics & Gynaecology"],
            },
        ]

        hosp_objs = []
        for h_data in hospitals_data:
            specs = h_data.pop('specs')
            hosp, _ = Hospital.objects.update_or_create(
                registration_number=h_data['registration_number'],
                defaults=h_data
            )
            for s_name in specs:
                if s_name in specialty_objs:
                    hosp.specialties.add(specialty_objs[s_name])
            hosp_objs.append(hosp)

        self.stdout.write(self.style.SUCCESS(f"Loaded {len(hosp_objs)} public hospitals."))

        # 3. Create Demo Users for each of the 3 roles

        # Role 3: Admin
        admin_user, _ = User.objects.get_or_create(
            username='admin',
            defaults={
                'first_name': 'Chief Medical',
                'last_name': 'Officer (CMO)',
                'email': 'cmo.raisen@sehatconnect.gov.in',
                'role': User.ROLE_ADMIN,
                'is_staff': True,
                'is_superuser': True,
                'phone_number': '9893012345',
            }
        )
        admin_user.set_password('admin123')
        admin_user.save()

        # Role 1: Health Workers (ASHA Workers)
        asha_1, _ = User.objects.get_or_create(
            username='asha_sunita',
            defaults={
                'first_name': 'Sunita',
                'last_name': 'Sharma',
                'email': 'sunita.asha@sehatconnect.in',
                'role': User.ROLE_HEALTH_WORKER,
                'phone_number': '9425098765',
                'employee_id': 'ASHA-MP-RSN-0104',
            }
        )
        asha_1.set_password('sunita123')
        asha_1.save()
        HealthWorkerProfile.objects.update_or_create(
            user=asha_1,
            defaults={
                'assigned_village': 'Salamatpur (सलामतपुर)',
                'panchayat': 'Salamatpur Gram Panchayat',
                'block': 'Sanchi',
                'district': 'Raisen',
                'qualification': 'ASHA Certified / 10th Pass + Health Training',
                'experience_years': 6,
                'asha_badge_number': 'ASHA-2021-081',
            }
        )

        asha_2, _ = User.objects.get_or_create(
            username='asha_anita',
            defaults={
                'first_name': 'Anita',
                'last_name': 'Bai',
                'email': 'anita.asha@sehatconnect.in',
                'role': User.ROLE_HEALTH_WORKER,
                'phone_number': '9425123456',
                'employee_id': 'ASHA-MP-RSN-0205',
            }
        )
        asha_2.set_password('anita123')
        asha_2.save()
        HealthWorkerProfile.objects.update_or_create(
            user=asha_2,
            defaults={
                'assigned_village': 'Kharwai (खरवई)',
                'panchayat': 'Kharwai Gram Panchayat',
                'block': 'Raisen',
                'district': 'Raisen',
                'qualification': 'Senior ASHA Sahayika / ANM Certified',
                'experience_years': 8,
                'asha_badge_number': 'ASHA-2019-142',
            }
        )

        # Role 2: Doctors / Medical Officers
        doctors_meta = [
            {
                'username': 'dr_sharma',
                'first_name': 'Dr. Alok',
                'last_name': 'Sharma',
                'email': 'dr.alok@sehatconnect.in',
                'phone': '9826011223',
                'license': 'MCI-MP-2015-8842',
                'qualification': 'MBBS, MD (Medicine)',
                'hospital': hosp_objs[0],  # DH Raisen
                'specialty': specialty_objs["General Medicine"],
                'room': 'OPD Room 4',
                'days': 'Mon, Tue, Wed, Thu, Fri, Sat',
                'start': '09:00:00',
                'end': '14:00:00',
            },
            {
                'username': 'dr_priya',
                'first_name': 'Dr. Priya',
                'last_name': 'Mehta',
                'email': 'dr.priya@sehatconnect.in',
                'phone': '9826033445',
                'license': 'MCI-MP-2018-4421',
                'qualification': 'MBBS, MS (Obstetrics & Gynaecology)',
                'hospital': hosp_objs[0],  # DH Raisen
                'specialty': specialty_objs["Obstetrics & Gynaecology"],
                'room': 'MCH Ward Room 1',
                'days': 'Mon, Tue, Wed, Thu, Fri',
                'start': '09:30:00',
                'end': '13:30:00',
            },
            {
                'username': 'dr_rajesh',
                'first_name': 'Dr. Rajesh',
                'last_name': 'Verma',
                'email': 'dr.rajesh@sehatconnect.in',
                'phone': '9826055667',
                'license': 'MCI-MP-2012-1190',
                'qualification': 'MBBS, DCH (Pediatrics)',
                'hospital': hosp_objs[1],  # CHC Sanchi
                'specialty': specialty_objs["Pediatrics"],
                'room': 'Child OPD Room 2',
                'days': 'Mon, Tue, Wed, Thu, Fri, Sat',
                'start': '09:00:00',
                'end': '14:00:00',
            },
            {
                'username': 'dr_neha',
                'first_name': 'Dr. Neha',
                'last_name': 'Tiwari',
                'email': 'dr.neha@sehatconnect.in',
                'phone': '9826077889',
                'license': 'MCI-MP-2020-5599',
                'qualification': 'MBBS (Medical Officer)',
                'hospital': hosp_objs[2],  # PHC Salamatpur
                'specialty': specialty_objs["General Medicine"],
                'room': 'Doctor Chamber',
                'days': 'Mon, Tue, Wed, Thu, Fri, Sat',
                'start': '10:00:00',
                'end': '16:00:00',
            },
        ]

        doctor_users = []
        for dm in doctors_meta:
            doc_user, _ = User.objects.get_or_create(
                username=dm['username'],
                defaults={
                    'first_name': dm['first_name'],
                    'last_name': dm['last_name'],
                    'email': dm['email'],
                    'role': User.ROLE_DOCTOR,
                    'phone_number': dm['phone'],
                }
            )
            # Default doctor password is username without dr_ + 123 e.g. sharma123, priya123
            pwd = dm['username'].replace('dr_', '') + '123'
            doc_user.set_password(pwd)
            doc_user.save()

            DoctorProfile.objects.update_or_create(
                user=doc_user,
                defaults={
                    'hospital': dm['hospital'],
                    'specialty': dm['specialty'],
                    'license_number': dm['license'],
                    'qualification': dm['qualification'],
                    'room_number': dm['room'],
                    'opd_days': dm['days'],
                    'opd_start_time': dm['start'],
                    'opd_end_time': dm['end'],
                    'max_daily_patients': 35,
                    'is_available': True,
                }
            )
            doctor_users.append(doc_user)

        self.stdout.write(self.style.SUCCESS("Created demo accounts for Admin, Health Workers (Sunita, Anita), and Doctors (Dr. Sharma, Dr. Priya, Dr. Rajesh, Dr. Neha)."))

        # 4. Create Realistic Rural Patients
        patients_data = [
            {
                'full_name': 'Ramesh Chandra Verma',
                'age': 54,
                'gender': 'male',
                'guardian_name': 'Late Ram Dayal Verma',
                'phone': '9876543210',
                'abha_id': '12-3456-7890-1122',
                'village': 'Salamatpur',
                'panchayat': 'Salamatpur',
                'block': 'Sanchi',
                'district': 'Raisen',
                'blood_group': 'B+',
                'allergies': 'Sulfa drugs',
                'chronic_conditions': 'Type-2 Diabetes, Hypertension (High BP)',
                'registered_by': asha_1,
                'vitals': {'bp_sys': 142, 'bp_dia': 92, 'pulse': 78, 'temp': 98.4, 'spo2': 97, 'sugar': 185, 'wt': 68.0, 'ht': 168.0},
            },
            {
                'full_name': 'Geeta Devi Lodhi',
                'age': 28,
                'gender': 'female',
                'guardian_name': 'Mukesh Lodhi (Husband)',
                'phone': '9876543211',
                'abha_id': '12-3456-7890-3344',
                'village': 'Gulgaon',
                'panchayat': 'Salamatpur',
                'block': 'Sanchi',
                'district': 'Raisen',
                'blood_group': 'O+',
                'allergies': 'None known',
                'chronic_conditions': 'Pregnancy - 3rd Trimester (High Risk - Moderate Anemia Hb 8.2)',
                'registered_by': asha_1,
                'vitals': {'bp_sys': 118, 'bp_dia': 76, 'pulse': 84, 'temp': 98.6, 'spo2': 99, 'sugar': 92, 'wt': 58.5, 'ht': 155.0},
            },
            {
                'full_name': 'Master Aarav Ahirwar',
                'age': 4,
                'gender': 'male',
                'guardian_name': 'Kailash Ahirwar (Father)',
                'phone': '9876543212',
                'abha_id': '',
                'village': 'Kharwai',
                'panchayat': 'Kharwai',
                'block': 'Raisen',
                'district': 'Raisen',
                'blood_group': 'A+',
                'allergies': 'None',
                'chronic_conditions': 'Recurrent chest congestion, Bronchial Asthma',
                'registered_by': asha_2,
                'vitals': {'bp_sys': 95, 'bp_dia': 60, 'pulse': 105, 'temp': 100.8, 'spo2': 94, 'sugar': 88, 'wt': 14.2, 'ht': 96.0},
            },
            {
                'full_name': 'Bhagwati Bai Sen',
                'age': 67,
                'gender': 'female',
                'guardian_name': 'Late Mohan Lal Sen',
                'phone': '9876543213',
                'abha_id': '12-3456-7890-5566',
                'village': 'Dewanganj',
                'panchayat': 'Dewanganj',
                'block': 'Sanchi',
                'district': 'Raisen',
                'blood_group': 'AB+',
                'allergies': 'NSAID painkillers cause stomach gastritis',
                'chronic_conditions': 'Severe Knee Osteoarthritis, Mild Cataract in left eye',
                'registered_by': asha_1,
                'vitals': {'bp_sys': 130, 'bp_dia': 84, 'pulse': 72, 'temp': 98.2, 'spo2': 98, 'sugar': 120, 'wt': 62.0, 'ht': 150.0},
            },
            {
                'full_name': 'Suresh Kumar Dhakad',
                'age': 42,
                'gender': 'male',
                'guardian_name': 'Babulal Dhakad',
                'phone': '9876543214',
                'abha_id': '12-3456-7890-7788',
                'village': 'Bairagarh Chichali',
                'panchayat': 'Kharwai',
                'block': 'Raisen',
                'district': 'Raisen',
                'blood_group': 'O-',
                'allergies': 'None',
                'chronic_conditions': 'Suspected Pulmonary Tuberculosis (Cough > 3 weeks, evening chills)',
                'registered_by': asha_2,
                'vitals': {'bp_sys': 110, 'bp_dia': 70, 'pulse': 88, 'temp': 99.8, 'spo2': 96, 'sugar': 105, 'wt': 51.0, 'ht': 170.0},
            },
        ]

        patient_objs = []
        for pd in patients_data:
            v_data = pd.pop('vitals')
            pat, created = Patient.objects.get_or_create(
                phone=pd['phone'],
                defaults=pd
            )
            patient_objs.append(pat)

            # Record initial vitals
            if not pat.vitals.exists():
                PatientVital.objects.create(
                    patient=pat,
                    blood_pressure_systolic=v_data['bp_sys'],
                    blood_pressure_diastolic=v_data['bp_dia'],
                    pulse_rate=v_data['pulse'],
                    body_temperature=v_data['temp'],
                    spo2=v_data['spo2'],
                    blood_sugar=v_data['sugar'],
                    weight_kg=v_data['wt'],
                    height_cm=v_data['ht'],
                    notes="Baseline village screening recorded during routine ASHA home visit.",
                    recorded_by=pat.registered_by
                )

        self.stdout.write(self.style.SUCCESS(f"Registered {len(patient_objs)} rural patients with baseline vitals."))

        # 5. Create Sample Appointments across dates
        today = timezone.now().date()
        
        # Today's appointments (OPD queue for Dr. Sharma and Dr. Priya)
        today_appts = [
            {
                'patient': patient_objs[0],  # Ramesh
                'doctor': doctor_users[0],   # Dr. Sharma
                'hospital': hosp_objs[0],    # DH Raisen
                'appointment_date': today,
                'time_slot': '09:00 AM - 09:30 AM',
                'token_number': 1,
                'urgency': 'normal',
                'status': 'confirmed',
                'symptoms': 'Routine diabetes and blood pressure checkup; morning fasting sugar levels elevated.',
                'booked_by': asha_1,
            },
            {
                'patient': patient_objs[1],  # Geeta Devi
                'doctor': doctor_users[1],   # Dr. Priya (Gynae)
                'hospital': hosp_objs[0],    # DH Raisen
                'appointment_date': today,
                'time_slot': '10:00 AM - 10:30 AM',
                'token_number': 2,
                'urgency': 'urgent',
                'status': 'confirmed',
                'symptoms': '34 weeks gestation, pedal edema, complaints of dizziness and low energy.',
                'booked_by': asha_1,
            },
            {
                'patient': patient_objs[2],  # Aarav (Child)
                'doctor': doctor_users[2],   # Dr. Rajesh (Pediatrics)
                'hospital': hosp_objs[1],    # CHC Sanchi
                'appointment_date': today,
                'time_slot': '09:30 AM - 10:00 AM',
                'token_number': 1,
                'urgency': 'urgent',
                'status': 'pending',
                'symptoms': 'High fever 101°F, persistent dry barking cough and wheezing for past 2 days.',
                'booked_by': asha_2,
            },
            {
                'patient': patient_objs[3],  # Bhagwati Bai
                'doctor': doctor_users[0],   # Dr. Sharma
                'hospital': hosp_objs[0],    # DH Raisen
                'appointment_date': today + timedelta(days=2),
                'time_slot': '11:00 AM - 11:30 AM',
                'token_number': 3,
                'urgency': 'normal',
                'status': 'confirmed',
                'symptoms': 'Severe pain in bilateral knees, difficulty walking to fields, requests pain relief.',
                'booked_by': asha_1,
            },
            {
                'patient': patient_objs[4],  # Suresh (TB suspect)
                'doctor': doctor_users[3],   # Dr. Neha (PHC Salamatpur)
                'hospital': hosp_objs[2],    # PHC Salamatpur
                'appointment_date': today - timedelta(days=3),
                'time_slot': '10:00 AM - 10:30 AM',
                'token_number': 1,
                'urgency': 'urgent',
                'status': 'completed',
                'symptoms': 'Chronic cough, blood streaked sputum once, night sweats and marked weight loss.',
                'booked_by': asha_2,
                'doctor_notes': 'Chest examination reveals bilateral crepitations. Referred for CBNAAT / GeneXpert sputum testing and chest X-Ray under National TB Elimination Program (NTEP).',
                'prescription': '1. Sputum CBNAAT Test (Govt Free)\n2. Cap Amoxicillin 500mg TDS x 5 days\n3. Syp Ambroxol 10ml TDS\n4. Review after sputum test report',
                'follow_up_date': today + timedelta(days=7),
            },
        ]

        for ad in today_appts:
            if not Appointment.objects.filter(patient=ad['patient'], doctor=ad['doctor'], appointment_date=ad['appointment_date']).exists():
                appt = Appointment(**ad)
                appt.save()

        self.stdout.write(self.style.SUCCESS("Generated sample OPD appointments with tokens and doctor schedules."))

        # 6. Create Sample Inter-Facility Referrals
        referrals_data = [
            {
                'patient': patient_objs[1],  # Geeta Devi (ANC risk)
                'from_hospital': hosp_objs[2],  # From PHC Salamatpur
                'to_hospital': hosp_objs[0],    # To DH Raisen (MCH wing)
                'target_specialty': specialty_objs["Obstetrics & Gynaecology"],
                'assigned_doctor': doctor_users[1], # Dr. Priya
                'referral_reason': 'High-Risk Pregnancy: Severe gestational anemia (Hb 8.2 g/dL) requiring IV Iron Sucrose infusion and ultrasound fetal biometry.',
                'clinical_summary': 'Primigravida, 34 weeks gestation. Fundal height matches dates. BP 118/76. Mild pedal edema present. Advised higher institutional care.',
                'urgency': 'urgent',
                'transport_required': False,
                'transport_status': 'not_needed',
                'status': 'accepted',
                'referred_by': asha_1,
                'hospital_remarks': 'Patient admitted to Antenatal Ward Bed #12. Iron Sucrose scheduled.',
            },
            {
                'patient': patient_objs[4],  # Suresh (TB / Respiratory)
                'from_hospital': hosp_objs[2],  # From PHC Salamatpur
                'to_hospital': hosp_objs[3],    # To Vidisha Medical College
                'target_specialty': specialty_objs["General Medicine"],
                'referral_reason': 'Suspected MDR-TB / Hemoptysis requiring Bronchoscopy & Advanced Pulmonology evaluation.',
                'clinical_summary': '42M with 3 weeks productive cough, episodic hemoptysis, SpO2 94% on room air. Sputum smear AFB positive.',
                'urgency': 'emergency',
                'transport_required': True,
                'transport_status': 'dispatched',
                'status': 'in_transit',
                'referred_by': asha_2,
                'hospital_remarks': 'Govt Dial 108 Ambulance dispatched from District Hub at 14:15. Emergency Pulmonology team alerted.',
            },
            {
                'patient': patient_objs[3],  # Bhagwati Bai (Elderly Ortho)
                'from_hospital': hosp_objs[1],  # From CHC Sanchi
                'to_hospital': hosp_objs[0],    # To DH Raisen
                'target_specialty': specialty_objs["Orthopaedics"],
                'referral_reason': 'Grade IV Knee Osteoarthritis needing Orthopedic consultation for physiotherapy and intra-articular injection or surgical evaluation.',
                'clinical_summary': '67F with non-weight bearing bilateral knee crepitus. Pain score 8/10 on standing.',
                'urgency': 'routine',
                'transport_required': False,
                'transport_status': 'not_needed',
                'status': 'pending',
                'referred_by': asha_1,
            },
        ]

        for rd in referrals_data:
            if not Referral.objects.filter(patient=rd['patient'], to_hospital=rd['to_hospital']).exists():
                ref = Referral(**rd)
                ref.save()

        self.stdout.write(self.style.SUCCESS("Generated sample inter-facility referrals with 108 ambulance coordination."))
        self.stdout.write(self.style.SUCCESS("=== SEEDING COMPLETED SUCCESSFULLY! ==="))
        self.stdout.write(self.style.NOTICE(
            "\nDefault Credentials for Testing:\n"
            "--------------------------------------------------\n"
            "1. Health Worker:  Username: asha_sunita  | Password: sunita123\n"
            "2. Doctor:         Username: dr_sharma    | Password: sharma123\n"
            "3. Administrator:  Username: admin        | Password: admin123\n"
            "--------------------------------------------------\n"
        ))
