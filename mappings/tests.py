from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from patients.models import Patient
from doctors.models import Doctor
from .models import PatientDoctorMapping


class MappingAPITests(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='password123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='password123'
        )

        self.patient1 = Patient.objects.create(
            user=self.user1,
            name='Patient One',
            age=35,
            gender='Female'
        )
        self.patient2 = Patient.objects.create(
            user=self.user2,
            name='Patient Two',
            age=45,
            gender='Male'
        )

        self.doctor1 = Doctor.objects.create(
            name='Dr. Strange',
            specialization='Surgery',
            experience=20
        )
        self.doctor2 = Doctor.objects.create(
            name='Dr. House',
            specialization='Diagnostics',
            experience=22
        )

        self.mapping1 = PatientDoctorMapping.objects.create(
            patient=self.patient1,
            doctor=self.doctor1
        )

        self.url = '/api/mappings/'

    def test_unauthenticated_access_denied(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_mapping_creation_success(self):
        self.client.force_authenticate(user=self.user1)
        payload = {
            'patient': self.patient1.id,
            'doctor': self.doctor2.id
        }
        response = self.client.post(self.url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['patient'], self.patient1.id)
        self.assertEqual(response.data['doctor'], self.doctor2.id)
        self.assertEqual(response.data['patient_name'], self.patient1.name)
        self.assertEqual(response.data['doctor_name'], self.doctor2.name)

    def test_user_cannot_map_another_users_patient(self):
        # user2 tries to create mapping for patient1 (owned by user1)
        self.client.force_authenticate(user=self.user2)
        payload = {
            'patient': self.patient1.id,
            'doctor': self.doctor1.id
        }
        response = self.client.post(self.url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('patient', response.data)

    def test_duplicate_mapping_rejected(self):
        # patient1 is already mapped to doctor1 in setUp
        self.client.force_authenticate(user=self.user1)
        payload = {
            'patient': self.patient1.id,
            'doctor': self.doctor1.id
        }
        response = self.client.post(self.url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_mappings_list_ownership_isolation(self):
        # user2 should see 0 mappings
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

        # user1 should see 1 mapping (mapping1)
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.mapping1.id)

    def test_filter_mappings_by_patient_id(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(f'{self.url}?patient_id={self.patient1.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        # user2 querying patient_id of user1's patient should return empty list
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(f'{self.url}?patient_id={self.patient1.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_mapping_delete_by_owner(self):
        self.client.force_authenticate(user=self.user1)
        detail_url = f'{self.url}{self.mapping1.id}/'
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(PatientDoctorMapping.objects.filter(id=self.mapping1.id).exists())

    def test_filter_mappings_by_doctor_id(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(f'{self.url}?doctor_id={self.doctor1.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['doctor'], self.doctor1.id)

    def test_invalid_patient_id_filter_returns_400(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(f'{self.url}?patient_id=abc')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('patient_id', response.data)

    def test_invalid_doctor_id_filter_returns_400(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(f'{self.url}?doctor_id=invalid_id')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('doctor_id', response.data)

    def test_user_cannot_update_other_users_mapping(self):
        self.client.force_authenticate(user=self.user2)
        detail_url = f'{self.url}{self.mapping1.id}/'
        response = self.client.patch(detail_url, {'doctor': self.doctor2.id})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_cannot_delete_other_users_mapping(self):
        self.client.force_authenticate(user=self.user2)
        detail_url = f'{self.url}{self.mapping1.id}/'
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(PatientDoctorMapping.objects.filter(id=self.mapping1.id).exists())

    def test_invalid_nonexistent_foreign_keys_rejected(self):
        self.client.force_authenticate(user=self.user1)
        payload = {
            'patient': 999999,
            'doctor': self.doctor1.id
        }
        response = self.client.post(self.url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('patient', response.data)

        payload2 = {
            'patient': self.patient1.id,
            'doctor': 999999
        }
        response2 = self.client.post(self.url, payload2)
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('doctor', response2.data)

    def test_staff_can_view_all_mappings(self):
        staff_user = User.objects.create_user(
            username='staffadmin',
            email='staffadmin@example.com',
            password='password123',
            is_staff=True
        )
        PatientDoctorMapping.objects.create(patient=self.patient2, doctor=self.doctor2)

        self.client.force_authenticate(user=staff_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

