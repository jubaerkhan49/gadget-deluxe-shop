from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User


class AccountsFlowTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='jubaer',
            email='jubaer@example.com',
            password='Password123!',
            first_name='Jubaer Khan'
        )

    def test_login_flow(self):
        login_url = reverse('accounts:login')
        response = self.client.post(login_url, {
            'username': 'jubaer',
            'password': 'Password123!'
        })
        self.assertEqual(response.status_code, 302)
        # Check profile page after login
        profile_res = self.client.get(reverse('accounts:profile'))
        self.assertEqual(profile_res.status_code, 200)
        self.assertContains(profile_res, "Jubaer Khan")

    def test_registration_flow(self):
        register_url = reverse('accounts:register')
        post_data = {
            'username': 'tanvir2026',
            'first_name': 'Tanvir Ahmed',
            'email': 'tanvir@example.com',
            'phone': '01812345678',
            'password1': 'MySecurePass123!',
            'password2': 'MySecurePass123!',
        }
        response = self.client.post(register_url, post_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='tanvir2026').exists())

    def test_logout_flow(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('accounts:logout'))
        self.assertEqual(response.status_code, 302)
