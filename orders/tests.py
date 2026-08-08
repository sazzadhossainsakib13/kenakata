from django.test import TestCase
from django.contrib.auth.models import User
from decimal import Decimal
from catalog.models import Category, Product
from orders.models import Order, OrderItem
from cart.models import Cart, CartItem


class OrderSecurityAndCheckoutValidationTest(TestCase):
    def setUp(self):
        self.user_a = User.objects.create_user(username='usera@example.com', email='usera@example.com', password='password123')
        self.user_b = User.objects.create_user(username='userb@example.com', email='userb@example.com', password='password123')
        self.staff_user = User.objects.create_user(username='staff@example.com', email='staff@example.com', password='password123', is_staff=True)
        
        self.category = Category.objects.create(name='Electronics')
        self.product = Product.objects.create(
            name='Smartphone',
            category=self.category,
            regular_price=Decimal('20000.00'),
            stock=5,
            active=True
        )
        self.order_a = Order.objects.create(
            user=self.user_a,
            recipient_name='User A',
            mobile='01712345678',
            division='Dhaka',
            district='Dhaka',
            full_address='House 1, Road 2, Dhaka',
            subtotal=Decimal('20000.00'),
            shipping_cost=Decimal('60.00'),
            total=Decimal('20060.00'),
            payment_method='Cash on Delivery',
            payment_status='pending',
            status='pending'
        )
        OrderItem.objects.create(
            order=self.order_a,
            product=self.product,
            product_name=self.product.name,
            unit_price=self.product.selling_price,
            quantity=1,
            subtotal=self.product.selling_price
        )

    # --- IDOR and Access Control Tests ---
    def test_user_a_can_view_own_order_and_success(self):
        self.client.login(username='usera@example.com', password='password123')
        response = self.client.get(f'/account/orders/{self.order_a.order_number}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.order_a.order_number)

        success_resp = self.client.get(f'/checkout/success/{self.order_a.order_number}/')
        self.assertEqual(success_resp.status_code, 200)
        self.assertContains(success_resp, self.order_a.order_number)

    def test_user_b_cannot_view_user_a_order_idor(self):
        self.client.login(username='userb@example.com', password='password123')
        response = self.client.get(f'/account/orders/{self.order_a.order_number}/')
        self.assertEqual(response.status_code, 404)

        receipt_resp = self.client.get(f'/checkout/receipt/{self.order_a.order_number}/')
        self.assertEqual(receipt_resp.status_code, 404)

        success_resp = self.client.get(f'/checkout/success/{self.order_a.order_number}/')
        self.assertEqual(success_resp.status_code, 404)

    def test_anonymous_cannot_access_order_endpoints(self):
        endpoints = [
            f'/account/orders/{self.order_a.order_number}/',
            f'/checkout/receipt/{self.order_a.order_number}/',
            f'/checkout/success/{self.order_a.order_number}/',
            f'/checkout/orders/{self.order_a.order_number}/',
            f'/checkout/order-confirmation/{self.order_a.order_number}/',
        ]
        for url in endpoints:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)
            self.assertIn('/auth/login/', response.url)

    def test_invalid_order_returns_404_and_does_not_reveal_latest_order(self):
        self.client.login(username='usera@example.com', password='password123')
        response = self.client.get('/account/orders/NONEXISTENT-99999/')
        self.assertEqual(response.status_code, 404)

        success_resp = self.client.get('/checkout/success/NONEXISTENT-99999/')
        self.assertEqual(success_resp.status_code, 404)

    def test_staff_can_view_order_details(self):
        self.client.login(username='staff@example.com', password='password123')
        response = self.client.get(f'/account/orders/{self.order_a.order_number}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.order_a.order_number)

    # --- Checkout Validation & Runtime Bug Tests ---
    def test_checkout_validation_failures_return_200_with_errors_no_500(self):
        self.client.login(username='usera@example.com', password='password123')
        cart = Cart.objects.create(user=self.user_a)
        CartItem.objects.create(cart=cart, product=self.product, quantity=2)

        # 1. Missing recipient name
        resp1 = self.client.post('/checkout/', {
            'recipient_name': '',
            'mobile': '01712345678',
            'division': 'Dhaka',
            'district': 'Dhaka',
        })
        self.assertEqual(resp1.status_code, 200)
        self.assertIn('field_errors', resp1.context)
        self.assertIn('recipient_name', resp1.context['field_errors'])
        self.assertEqual(cart.items.count(), 1)  # Cart intact

        # 2. Missing mobile
        resp2 = self.client.post('/checkout/', {
            'recipient_name': 'Test User',
            'mobile': '',
            'division': 'Dhaka',
            'district': 'Dhaka',
        })
        self.assertEqual(resp2.status_code, 200)
        self.assertIn('mobile', resp2.context['field_errors'])

        # 3. Invalid mobile format
        resp3 = self.client.post('/checkout/', {
            'recipient_name': 'Test User',
            'mobile': '12345ABC',
            'division': 'Dhaka',
            'district': 'Dhaka',
        })
        self.assertEqual(resp3.status_code, 200)
        self.assertIn('mobile', resp3.context['field_errors'])

        # 4. Missing division
        resp4 = self.client.post('/checkout/', {
            'recipient_name': 'Test User',
            'mobile': '01712345678',
            'division': '',
            'district': 'Dhaka',
        })
        self.assertEqual(resp4.status_code, 200)
        self.assertIn('division', resp4.context['field_errors'])

        # 5. Missing district
        resp5 = self.client.post('/checkout/', {
            'recipient_name': 'Test User',
            'mobile': '01712345678',
            'division': 'Dhaka',
            'district': '',
        })
        self.assertEqual(resp5.status_code, 200)
        self.assertIn('district', resp5.context['field_errors'])

    def test_successful_checkout_deducts_stock_atomically(self):
        self.client.login(username='usera@example.com', password='password123')
        cart = Cart.objects.create(user=self.user_a)
        CartItem.objects.create(cart=cart, product=self.product, quantity=2)
        initial_stock = self.product.stock

        response = self.client.post('/checkout/', {
            'recipient_name': 'Valid User',
            'mobile': '+880 1712-345678',
            'division': 'Dhaka',
            'district': 'Dhaka',
            'house': '12',
            'road': '4',
        })
        self.assertEqual(response.status_code, 302)
        
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, initial_stock - 2)
        self.assertEqual(cart.items.count(), 0)  # Cart cleared on success
