from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Doctor


class DoctorAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='doctoruser',
            email='docuser@example.com',
            password='password123'
        )
        self.doctor = Doctor.objects.create(
            name='Dr. Smith',
            specialization='Cardiology',
            experience=15
        )
        self.url = '/api/doctors/'

    def test_unauthenticated_access_denied(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_doctor_creation(self):
        self.client.force_authenticate(user=self.user)
        payload = {
            'name': 'Dr. Adams',
            'specialization': 'Neurology',
            'experience': 10
        }
        response = self.client.post(self.url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Dr. Adams')
        self.assertEqual(response.data['specialization'], 'Neurology')
        self.assertEqual(response.data['experience'], 10)

    def test_negative_experience_validation(self):
        self.client.force_authenticate(user=self.user)
        payload = {
            'name': 'Dr. Invalid',
            'specialization': 'Pediatrics',
            'experience': -2
        }
        response = self.client.post(self.url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('experience', response.data)

    def test_blank_name_validation(self):
        self.client.force_authenticate(user=self.user)
        payload = {
            'name': '   ',
            'specialization': 'Pediatrics',
            'experience': 5
        }
        response = self.client.post(self.url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)

    def test_doctor_filtering_by_specialization(self):
        Doctor.objects.create(
            name='Dr. Watson',
            specialization='Orthopedics',
            experience=8
        )
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'{self.url}?specialization=Cardio')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Dr. Smith')

    def test_doctor_update_and_delete(self):
        self.client.force_authenticate(user=self.user)
        detail_url = f'{self.url}{self.doctor.id}/'
        
        # Partial update
        patch_response = self.client.patch(detail_url, {'experience': 16})
        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)
        self.doctor.refresh_from_db()
        self.assertEqual(self.doctor.experience, 16)

        # Delete
        delete_response = self.client.delete(detail_url)
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Doctor.objects.filter(id=self.doctor.id).exists())

    def test_retrieve_doctor_detail(self):
        self.client.force_authenticate(user=self.user)
        detail_url = f'{self.url}{self.doctor.id}/'
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.doctor.id)
        self.assertEqual(response.data['name'], self.doctor.name)

    def test_doctor_search_by_name(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'{self.url}?search=Smith')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Dr. Smith')

    def test_doctor_search_by_specialization(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'{self.url}?search=Cardio')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['specialization'], 'Cardiology')

    def test_blank_specialization_validation(self):
        self.client.force_authenticate(user=self.user)
        payload = {
            'name': 'Dr. NoSpec',
            'specialization': '   ',
            'experience': 5
        }
        response = self.client.post(self.url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('specialization', response.data)

    def test_excessive_experience_validation(self):
        self.client.force_authenticate(user=self.user)
        payload = {
            'name': 'Dr. Ancient',
            'specialization': 'General Medicine',
            'experience': 80
        }
        response = self.client.post(self.url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('experience', response.data)

    def test_whitespace_search_query_returns_all(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'{self.url}?search=   ')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

