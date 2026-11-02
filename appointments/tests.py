from datetime import timedelta
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone
from accounts.models import User, DoctorProfile, HealthWorkerProfile
from appointments.models import Appointment
from hospitals.models import Hospital, Specialty
from patients.models import Patient


class AppointmentModelTests(TestCase):
    def setUp(self):
        self.hospital = Hospital.objects.create(
            name="Raisen District Hospital",
            facility_type="dh",
            registration_number="DH-RSN-TEST",
            address="Civil Lines",
            village_town="Raisen",
            block="Raisen",
            district="Raisen",
            pincode="464551",
            contact_phone="07482-222108",
            latitude=23.33,
            longitude=77.78,
        )
        self.specialty = Specialty.objects.create(name="General Medicine")
        
        self.doctor_user = User.objects.create_user(
            username="dr_test",
            password="testpassword",
            role=User.ROLE_DOCTOR
        )
        DoctorProfile.objects.create(
            user=self.doctor_user,
            hospital=self.hospital,
            specialty=self.specialty,
            license_number="LIC-1234",
            is_available=True
        )

        self.worker_user = User.objects.create_user(
            username="asha_test",
            password="testpassword",
            role=User.ROLE_HEALTH_WORKER
        )

        self.patient = Patient.objects.create(
            full_name="Ramesh Verma",
            age=50,
            gender="male",
            village="Salamatpur",
            block="Sanchi",
            district="Raisen",
            phone="9876543210",
            registered_by=self.worker_user
        )

    def test_appointment_creation_and_token(self):
        tomorrow = timezone.now().date() + timedelta(days=1)
        appt = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor_user,
            hospital=self.hospital,
            appointment_date=tomorrow,
            time_slot="09:00 AM - 09:30 AM",
            symptoms="Mild fever and body ache",
            booked_by=self.worker_user
        )
        self.assertEqual(appt.token_number, 1)
        self.assertTrue(appt.appointment_number.startswith("APT-"))
        self.assertTrue(len(appt.generate_qr_code_base64()) > 0)

    def test_duplicate_slot_prevention(self):
        tomorrow = timezone.now().date() + timedelta(days=1)
        # Create first appointment
        Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor_user,
            hospital=self.hospital,
            appointment_date=tomorrow,
            time_slot="09:00 AM - 09:30 AM",
            symptoms="Fever",
            booked_by=self.worker_user
        )

        # Create another patient
        patient2 = Patient.objects.create(
            full_name="Suresh Kumar",
            age=40,
            gender="male",
            village="Kharwai",
            block="Raisen",
            district="Raisen",
            registered_by=self.worker_user
        )

        # Attempt to book same doctor on same date and same time slot
        duplicate_appt = Appointment(
            patient=patient2,
            doctor=self.doctor_user,
            hospital=self.hospital,
            appointment_date=tomorrow,
            time_slot="09:00 AM - 09:30 AM",
            symptoms="Cough",
            booked_by=self.worker_user
        )

        with self.assertRaises(ValidationError):
            duplicate_appt.clean()
