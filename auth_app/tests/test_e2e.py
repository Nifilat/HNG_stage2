from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from ..models import User, Organisation

class RegisterEndpointTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_successful_registration(self):
        data = {
            "firstName": "John",
            "lastName": "Doe",
            "email": "john@example.com",
            "password": "strongpassword",
            "phone": "1234567890"
        }
        response = self.client.post('/auth/register', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(response.data['message'], 'Registration successful')
        self.assertIn('accessToken', response.data['data'])
        self.assertIn('user', response.data['data'])

        # Check if default organisation was created
        user = User.objects.get(email='john@example.com')
        org = Organisation.objects.filter(users=user).first()
        self.assertIsNotNone(org)
        self.assertEqual(org.name, "John's Organisation")


    def test_missing_required_fields(self):
        required_fields = ['firstName', 'lastName', 'email', 'password']
        for field in required_fields:
            data = {
                "firstName": "John",
                "lastName": "Doe",
                "email": "john@example.com",
                "password": "strongpassword",
            }
            data.pop(field)
            response = self.client.post('/auth/register', data, format='json')
            self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
            self.assertIn(field, response.data['errors'])

    def test_duplicate_email(self):
        User.objects.create_user(email='john@example.com', password='password', firstName='John', lastName='Doe')
        data = {
            "firstName": "John",
            "lastName": "Doe",
            "email": "john@example.com",
            "password": "strongpassword",
        }
        response = self.client.post('/auth/register', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertIn('email', response.data['errors'])

    def test_successful_login(self):
        # First, create a user
        User.objects.create_user(email='jane@example.com', password='strongpassword', firstName='Jane', lastName='Doe')
        
        data = {
            "email": "jane@example.com",
            "password": "strongpassword"
        }
        response = self.client.post('/auth/login', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(response.data['message'], 'Login successful')
        self.assertIn('accessToken', response.data['data'])
        self.assertIn('user', response.data['data'])

    
    def test_failed_login(self):
        data = {
            "email": "invalid@example.com",
            "password": "wrongpassword"
            }
        response = self.client.post('/auth/login', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['status'], 'error')
        self.assertEqual(response.data['message'], 'Invalid credentials')
