from django.test import TestCase
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta
from catalog.models import Category, Product
from cart.models import Cart, CartItem, Coupon


class CartLogicTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Groceries')
        self.product1 = Product.objects.create(
            name='Rice 5kg',
            category=self.category,
            regular_price=Decimal('500.00'),
            discount_price=Decimal('450.00'),
            stock=20,
            active=True
        )
        self.product2 = Product.objects.create(
            name='Mustard Oil 1L',
            category=self.category,
            regular_price=Decimal('250.00'),
            stock=15,
            active=True
        )
        self.cart = Cart.objects.create()
        self.coupon = Coupon.objects.create(
            code='TEST10',
            discount_type='percentage',
            discount_value=Decimal('10'),
            min_order_amount=Decimal('500'),
            is_active=True,
            expiry_date=timezone.now() + timedelta(days=10)
        )

    def test_cart_subtotal_calculation(self):
        CartItem.objects.create(cart=self.cart, product=self.product1, quantity=2) # 2 x 450 = 900
        CartItem.objects.create(cart=self.cart, product=self.product2, quantity=1) # 1 x 250 = 250
        self.assertEqual(self.cart.get_subtotal(), Decimal('1150.00'))

    def test_coupon_percentage_discount(self):
        CartItem.objects.create(cart=self.cart, product=self.product1, quantity=2) # subtotal 900
        self.cart.coupon = self.coupon
        self.cart.save()
        self.assertEqual(self.cart.get_coupon_discount(), Decimal('90.00'))
        self.assertEqual(self.cart.get_total(), Decimal('900.00') - Decimal('90.00') + Decimal('120.00'))

    def test_coupon_min_order_restriction(self):
        CartItem.objects.create(cart=self.cart, product=self.product2, quantity=1) # subtotal 250 < 500
        self.cart.coupon = self.coupon
        self.cart.save()
        self.assertEqual(self.cart.get_coupon_discount(), Decimal('0.00'))
