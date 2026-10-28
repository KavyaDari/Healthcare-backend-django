from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Patient


class PatientAPITests(APITestCase):
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
            name='John Doe',
            age=30,
            gender='Male'
        )

        self.url = '/api/patients/'

    def test_unauthenticated_access_denied(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_patient_creation(self):
        self.client.force_authenticate(user=self.user1)
        payload = {
            'name': 'Jane Doe',
            'age': 25,
            'gender': 'Female'
        }
        response = self.client.post(self.url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Jane Doe')
        self.assertEqual(response.data['user'], self.user1.id)

    def test_negative_age_validation(self):
        self.client.force_authenticate(user=self.user1)
        payload = {
            'name': 'Invalid Age Patient',
            'age': -5,
            'gender': 'Male'
        }
        response = self.client.post(self.url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('age', response.data)

    def test_excessive_age_validation(self):
        self.client.force_authenticate(user=self.user1)
        payload = {
            'name': 'Unrealistic Age Patient',
            'age': 150,
            'gender': 'Male'
        }
        response = self.client.post(self.url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('age', response.data)

    def test_blank_name_validation(self):
        self.client.force_authenticate(user=self.user1)
        payload = {
            'name': '   ',
            'age': 40,
            'gender': 'Male'
        }
        response = self.client.post(self.url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)

    def test_ownership_isolation_in_list(self):
        # user2 should not see user1's patient
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

        # user1 should see user1's patient
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.patient1.id)

    def test_user_cannot_access_other_users_patient_detail(self):
        self.client.force_authenticate(user=self.user2)
        detail_url = f'{self.url}{self.patient1.id}/'
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patient_owner_can_update_and_delete(self):
        self.client.force_authenticate(user=self.user1)
        detail_url = f'{self.url}{self.patient1.id}/'
        
        # Update
        patch_response = self.client.patch(detail_url, {'name': 'John Updated'})
        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)
        self.patient1.refresh_from_db()
        self.assertEqual(self.patient1.name, 'John Updated')

        # Delete
        delete_response = self.client.delete(detail_url)
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Patient.objects.filter(id=self.patient1.id).exists())

    def test_blank_gender_validation(self):
        self.client.force_authenticate(user=self.user1)
        payload = {
            'name': 'Sample Patient',
            'age': 30,
            'gender': '   '
        }
        response = self.client.post(self.url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('gender', response.data)

    def test_user_cannot_update_other_users_patient(self):
        self.client.force_authenticate(user=self.user2)
        detail_url = f'{self.url}{self.patient1.id}/'
        response = self.client.patch(detail_url, {'name': 'Hacked Name'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.patient1.refresh_from_db()
        self.assertEqual(self.patient1.name, 'John Doe')

    def test_user_cannot_delete_other_users_patient(self):
        self.client.force_authenticate(user=self.user2)
        detail_url = f'{self.url}{self.patient1.id}/'
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Patient.objects.filter(id=self.patient1.id).exists())

    def test_staff_can_view_all_patients(self):
        staff_user = User.objects.create_user(
            username='staffuser',
            email='staff@example.com',
            password='password123',
            is_staff=True
        )
        Patient.objects.create(user=self.user2, name='Patient 2', age=50, gender='Female')

        self.client.force_authenticate(user=staff_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_patient_owner_assigned_from_request_not_client_input(self):
        self.client.force_authenticate(user=self.user1)
        payload = {
            'name': 'Spoof Attempt',
            'age': 32,
            'gender': 'Male',
            'user': self.user2.id
        }
        response = self.client.post(self.url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['user'], self.user1.id)
        created_patient = Patient.objects.get(id=response.data['id'])
        self.assertEqual(created_patient.user, self.user1)

