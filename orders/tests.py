from django.test import TestCase
from django.contrib.auth.models import User
from decimal import Decimal
from catalog.models import Category, Product
from orders.models import Order, OrderItem


class OrderCreationAndAuthorizationTest(TestCase):
    def setUp(self):
        self.user_a = User.objects.create_user(username='usera@example.com', email='usera@example.com', password='password123')
        self.user_b = User.objects.create_user(username='userb@example.com', email='userb@example.com', password='password123')
        self.category = Category.objects.create(name='Electronics')
        self.product = Product.objects.create(
            name='Smartphone',
            category=self.category,
            regular_price=Decimal('20000.00'),
            stock=10,
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

    def test_cod_payment_status_defaults_to_pending(self):
        self.assertEqual(self.order_a.payment_method, 'Cash on Delivery')
        self.assertEqual(self.order_a.payment_status, 'pending')

    def test_user_a_can_view_own_order(self):
        self.client.login(username='usera@example.com', password='password123')
        response = self.client.get(f'/account/orders/{self.order_a.order_number}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.order_a.order_number)

    def test_user_b_cannot_view_user_a_order_idor(self):
        self.client.login(username='userb@example.com', password='password123')
        response = self.client.get(f'/account/orders/{self.order_a.order_number}/')
        self.assertEqual(response.status_code, 404)

    def test_anonymous_cannot_access_order_detail(self):
        response = self.client.get(f'/account/orders/{self.order_a.order_number}/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/auth/login/', response.url)

    def test_unauthorized_user_cannot_access_order_success(self):
        self.client.login(username='userb@example.com', password='password123')
        response = self.client.get(f'/checkout/success/{self.order_a.order_number}/')
        self.assertEqual(response.status_code, 302)
