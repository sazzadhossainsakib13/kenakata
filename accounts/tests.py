from django.test import TestCase
from django.contrib.auth.models import User
from django.core.cache import cache
from accounts.models import UserProfile
from accounts.utils import normalize_bd_mobile, validate_bd_mobile


class AccountsValidationAndNormalizationTest(TestCase):
    def test_valid_bd_mobile_normalization(self):
        cases = [
            ('01712345678', '01712345678'),
            ('+8801712345678', '01712345678'),
            ('8801712345678', '01712345678'),
            ('+880 1812-345678', '01812345678'),
            ('019 123 45678', '01912345678'),
            ('+880 (131) 2345678', '01312345678'),
        ]
        for raw, expected in cases:
            self.assertTrue(validate_bd_mobile(raw), f"Validation failed for {raw}")
            self.assertEqual(normalize_bd_mobile(raw), expected, f"Normalization mismatch for {raw}")

    def test_invalid_bd_mobile_rejection(self):
        invalid_numbers = [
            '017',             # Partial prefix
            '12345',           # Short number
            '01212345678',     # Invalid operator 012
            '+12345678901',    # Non-BD country code
            '01712345678901',  # Too long
            '0171234567a',     # Contains letters
            '',                # Empty
        ]
        for num in invalid_numbers:
            self.assertFalse(validate_bd_mobile(num), f"Should be invalid: {num}")
            self.assertIsNone(normalize_bd_mobile(num), f"Should normalize to None: {num}")


class AccountsSecurityAndAuthTest(TestCase):
    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(
            username='user@example.com',
            email='user@example.com',
            password='password123',
            first_name='Test',
            last_name='User'
        )
        UserProfile.objects.create(
            user=self.user,
            mobile='01712345678',
            division='dhaka'
        )

    def tearDown(self):
        cache.clear()

    # --- Authentication by Multi-Identifier ---
    def test_login_by_username(self):
        response = self.client.post('/auth/login/', {
            'email': 'user@example.com',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/account/')

    def test_login_by_normalized_mobile_formats(self):
        mobile_formats = [
            '01712345678',
            '+8801712345678',
            '8801712345678',
            '+880 1712-345678',
        ]
        for phone in mobile_formats:
            self.client.logout()
            cache.clear()
            response = self.client.post('/auth/login/', {
                'email': phone,
                'password': 'password123'
            })
            self.assertEqual(response.status_code, 302, f"Failed login with phone format: {phone}")

    def test_login_by_partial_phone_rejected(self):
        # Substring/partial match must NOT authenticate
        response = self.client.post('/auth/login/', {
            'email': '017',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid email or password.')

    # --- Open Redirect Prevention (C3) ---
    def test_open_redirect_local_succeeds(self):
        response = self.client.post('/auth/login/?next=/account/orders/', {
            'email': 'user@example.com',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/account/orders/')

    def test_open_redirect_external_urls_rejected(self):
        unsafe_urls = [
            'https://evil.com/phishing',
            '//evil.com/phishing',
            'javascript:alert(1)',
            'http://attacker.com',
        ]
        for unsafe in unsafe_urls:
            response = self.client.post(f'/auth/login/?next={unsafe}', {
                'email': 'user@example.com',
                'password': 'password123'
            })
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.url, '/account/')  # Safe fallback

    # --- Brute Force & Rate Limiting (C5) ---
    def test_login_rate_limiting_lockout_and_recovery(self):
        # 5 failed attempts
        for _ in range(5):
            self.client.post('/auth/login/', {
                'email': 'user@example.com',
                'password': 'wrongpassword'
            })
        # 6th attempt is locked out
        response = self.client.post('/auth/login/', {
            'email': 'user@example.com',
            'password': 'wrongpassword'
        })
        self.assertContains(response, 'temporarily locked')

        # Successful auth after lockout expires clears counter
        cache.clear()
        login_success = self.client.post('/auth/login/', {
            'email': 'user@example.com',
            'password': 'password123'
        })
        self.assertEqual(login_success.status_code, 302)

    # --- Account Enumeration Resistance ---
    def test_generic_login_failure_message(self):
        response_nonexistent = self.client.post('/auth/login/', {
            'email': 'nonexistent@example.com',
            'password': 'somepassword'
        })
        response_wrongpass = self.client.post('/auth/login/', {
            'email': 'user@example.com',
            'password': 'wrongpassword'
        })
        # Both produce identical neutral message
        self.assertEqual(response_nonexistent.status_code, 200)
        self.assertEqual(response_wrongpass.status_code, 200)
        self.assertContains(response_nonexistent, 'Invalid email or password.')
        self.assertContains(response_wrongpass, 'Invalid email or password.')
