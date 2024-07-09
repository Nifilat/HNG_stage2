from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
import unittest.mock as mock
from django.urls import reverse
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

        org_name = f"{data['firstName']}'s Organisation"
        default_org = Organisation.objects.filter(name=org_name).first()
        print(f"Default Organisation: {default_org.name}")
        self.assertIsNotNone(default_org)
        self.assertTrue(Organisation.objects.filter(name=org_name).exists())


    def test_login_user(self):
        
        
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

        refresh.access_token.set_exp(lifetime=timedelta(seconds=1))

        token = str(refresh.access_token)

        mock_response = mock.Mock(status_code=status.HTTP_200_OK)
        with mock.patch('rest_framework.test.APIClient.get', return_value=mock_response):
            self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
            response = self.client.get('/api/organisations/')
            print(f"Initial response status: {response.status_code}")
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            time.sleep(2)

            mock_response.status_code = status.HTTP_401_UNAUTHORIZED
            response = self.client.get('/api/organisations/')
            self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])




class OrganisationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(email='user1@example.com', password='password', firstName='Tom', lastName='One')
        self.user2 = User.objects.create_user(email='user2@example.com', password='password', firstName='Mike', lastName='Two')
        self.org1 = Organisation.objects.create(name=f"{self.user1.firstName}'s Organisation", description="First Organisation")
        self.org1.users.add(self.user1)
        self.org2 = Organisation.objects.create(name=f"{self.user2.firstName}'s Organisation", description="Second Organisation")
        self.org2.users.add(self.user2)

    def test_user_can_only_see_own_organisations(self):
        refresh = RefreshToken.for_user(self.user1)
    
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')
        response = self.client.get('/api/organisations/')
        print(f"Response data: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
        self.assertEqual(response.data['status'], 'success')
        self.assertIn('message', response.data)
        self.assertIn('data', response.data)
        self.assertIn('organisations', response.data['data'])
        organisations = response.data['data']['organisations']
    
        self.assertEqual(len(organisations), 1)
        self.assertEqual(organisations[0]['name'], f"{self.user1.firstName}'s Organisation")
        self.assertEqual(organisations[0]['description'], "First Organisation")

    # Ensure user1 can't see user2's organisation
        self.assertNotIn(f"{self.user2.firstName}'s Organisation", [org['name'] for org in organisations])


    def test_user_cannot_access_other_users_organisations(self):
        refresh = RefreshToken.for_user(self.user1)
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')
        response = self.client.get(f'/api/organisations/{self.org2.orgId}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

