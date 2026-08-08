from django.test import TestCase
from django.contrib.auth.models import User
from accounts.views import validate_bd_mobile


class AccountsValidationTest(TestCase):
    def test_valid_bd_mobile_numbers(self):
        valid_numbers = [
            '01712345678',
            '01812345678',
            '01912345678',
            '01312345678',
            '+8801712345678',
            '8801712345678',
        ]
        for num in valid_numbers:
            self.assertTrue(validate_bd_mobile(num), f"Failed for {num}")

    def test_invalid_bd_mobile_numbers(self):
        invalid_numbers = [
            '12345',
            '017ABC',
            '00000000000',
            '01212345678',
            '+12345678901',
        ]
        for num in invalid_numbers:
            self.assertFalse(validate_bd_mobile(num), f"Failed for {num}")


class AccountsAuthTest(TestCase):
    def setUp(self):
        from django.core.cache import cache
        cache.clear()
        self.user = User.objects.create_user(
            username='user@example.com',
            email='user@example.com',
            password='password123',
            first_name='Test',
            last_name='User'
        )

    def tearDown(self):
        from django.core.cache import cache
        cache.clear()

    def test_login_success(self):
        response = self.client.post('/auth/login/', {
            'email': 'user@example.com',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 302)

    def test_login_failure(self):
        response = self.client.post('/auth/login/', {
            'email': 'user@example.com',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid email or password.')

    def test_open_redirect_prevention(self):
        response = self.client.post('/auth/login/?next=https://evil.com/phishing', {
            'email': 'user@example.com',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/account/')

    def test_login_rate_limiting_lockout(self):
        # 5 failed attempts
        for _ in range(5):
            self.client.post('/auth/login/', {
                'email': 'user@example.com',
                'password': 'wrongpassword'
            })
        # 6th attempt should be locked out
        response = self.client.post('/auth/login/', {
            'email': 'user@example.com',
            'password': 'wrongpassword'
        })
        self.assertContains(response, 'temporarily locked')
