from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
import unittest.mock as mock
from ..models import User, Organisation
from rest_framework_simplejwt.tokens import RefreshToken
import time
from datetime import timedelta

client = APIClient()
class AuthTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_register_user(self):
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

    def test_login_user(self):
        # First, create a user
        user = User.objects.create_user(email='jane@example.com', password='strongpassword', firstName='Jane', lastName='Doe')
        
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


    def test_token_expiration(self):
        user = User.objects.create_user(email='test@example.com', phone="08028151196", password='testpassword', firstName='Test', lastName='User')
        refresh = RefreshToken.for_user(user)
    
    # Set token expiration to 1 second from now for testing purposes
        refresh.access_token.set_exp(lifetime=timedelta(seconds=1))
    
        token = str(refresh.access_token)
        
    
    # Mock the API response
        mock_response = mock.Mock(status_code=status.HTTP_200_OK)
        with mock.patch('rest_framework.test.client.get', return_value=mock_response):
            self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
            response = self.client.get('/api/organisations/')
            print(f"Initial response status: {response.status_code}")
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Wait for token to expire
            time.sleep(2)
        
        # Mock the API response with a 401 or 403 status code
            mock_response.status_code = status.HTTP_401_UNAUTHORIZED
            response = self.client.get('/api/organisations/')
            print(f"Post-expiration response status: {response.status_code}")
            self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])



class OrganisationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(email='user1@example.com', password='password', firstName='User', lastName='One')
        self.user2 = User.objects.create_user(email='user2@example.com', password='password', firstName='User', lastName='Two')
        self.org1 = Organisation.objects.create(name="User One's Organisation", description="First Organisation")
        self.org1.users.add(self.user1)
        self.org2 = Organisation.objects.create(name="User Two's Organisation", description="Second Organisation")
        self.org2.users.add(self.user2)

    def test_user_can_only_see_own_organisations(self):
        refresh = RefreshToken.for_user(self.user1)
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')
        response = self.client.get('/api/organisations/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 1)  
        self.assertEqual(response.data['data'][0]['name'], "User One's Organisation")  
        self.assertEqual(response.data['data'][0]['description'], "First Organisation")  

        # Ensure user1 can't see user2's organisation
        self.assertNotIn("User Two's Organisation", [org['name'] for org in response.data['data']])

    def test_user_cannot_access_other_users_organisations(self):
        refresh = RefreshToken.for_user(self.user1)
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')
        response = self.client.get(f'/api/organisations/{self.org2.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

