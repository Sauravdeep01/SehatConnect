from django.test import TestCase
from accounts.models import User
from patients.models import Patient, PatientVital


class PatientModelTests(TestCase):
    def setUp(self):
        self.worker = User.objects.create_user(
            username="asha_worker_test",
            password="password123",
            role=User.ROLE_HEALTH_WORKER
        )

    def test_patient_registration_and_id_generation(self):
        patient = Patient.objects.create(
            full_name="Geeta Devi",
            age=32,
            gender="female",
            village="Salamatpur",
            block="Sanchi",
            district="Raisen",
            registered_by=self.worker
        )
        self.assertTrue(patient.registration_id.startswith("SC-PAT-"))
        self.assertEqual(patient.gender_display, "Female")

    def test_patient_vitals_recording_and_bmi(self):
        patient = Patient.objects.create(
            full_name="Mohan Lal",
            age=45,
            gender="male",
            village="Gulgaon",
            block="Sanchi",
            district="Raisen",
            registered_by=self.worker
        )
        vital = PatientVital.objects.create(
            patient=patient,
            blood_pressure_systolic=130,
            blood_pressure_diastolic=85,
            pulse_rate=76,
            weight_kg=70.0,
            height_cm=170.0,
            recorded_by=self.worker
        )
        self.assertEqual(vital.bp_display, "130/85 mmHg")
        self.assertAlmostEqual(vital.bmi, 24.2, delta=0.2)
        self.assertEqual(patient.latest_vitals.id, vital.id)
