from django.test import TestCase
from django.contrib.auth.models import User
from decimal import Decimal
import json

from catalog.models import Category, Product
from pos.models import (
    StoreSettings, POSCustomer, POSSale, POSSaleItem,
    POSReturn, POSReturnItem, InventoryMovement
)


class POSTestCase(TestCase):
    def setUp(self):
        # Create users
        self.customer_user = User.objects.create_user(username='customer', password='password123')
        self.staff_user = User.objects.create_user(username='cashier', password='password123', is_staff=True)
        self.admin_user = User.objects.create_user(username='admin_pos', password='password123', is_staff=True, is_superuser=True)

        # Store settings
        self.settings = StoreSettings.get_settings()

        # Category & Products
        self.category = Category.objects.create(name='Electronics', icon='bi-cpu')
        self.product = Product.objects.create(
            name='Wireless Mouse',
            category=self.category,
            regular_price=Decimal('1200.00'),
            discount_price=Decimal('1000.00'),
            stock=10,
            active=True,
            barcode='894123456789'
        )

        # POS Customer
        self.pos_customer = POSCustomer.objects.create(
            name='Rahim Uddin',
            mobile='01711112222',
            email='rahim@example.com'
        )

    def test_customer_blocked_from_pos(self):
        self.client.login(username='customer', password='password123')
        response = self.client.get('/pos/')
        self.assertEqual(response.status_code, 302)

    def test_staff_allowed_access_to_pos(self):
        self.client.login(username='cashier', password='password123')
        response = self.client.get('/pos/')
        self.assertEqual(response.status_code, 200)

    def test_product_search_by_barcode(self):
        self.client.login(username='cashier', password='password123')
        response = self.client.get('/pos/search-products/?q=894123456789')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(len(data['products']), 1)
        self.assertEqual(data['products'][0]['name'], 'Wireless Mouse')

    def test_complete_pos_sale_success(self):
        self.client.login(username='cashier', password='password123')
        payload = {
            'items': [{'product_id': self.product.id, 'quantity': 2}], # 2 x 1000 = 2000
            'customer_id': self.pos_customer.id,
            'discount_type': 'none',
            'discount_value': 0,
            'cash_received': 2000,
            'notes': 'Test Cash Sale'
        }
        response = self.client.post(
            '/pos/complete-sale/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])

        # Verify DB changes
        sale = POSSale.objects.get(receipt_number=data['receipt_number'])
        self.assertEqual(sale.total, Decimal('2000.00'))
        self.assertEqual(sale.cashier, self.staff_user)

        # Stock deduction verification (10 - 2 = 8)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 8)

        # InventoryMovement log verification
        movement = InventoryMovement.objects.filter(reference_id=sale.receipt_number).first()
        self.assertIsNotNone(movement)
        self.assertEqual(movement.movement_type, 'POS_SALE')
        self.assertEqual(movement.quantity, -2)

    def test_insufficient_cash_rejected(self):
        self.client.login(username='cashier', password='password123')
        payload = {
            'items': [{'product_id': self.product.id, 'quantity': 1}], # 1000
            'customer_id': None,
            'discount_type': 'none',
            'discount_value': 0,
            'cash_received': 500, # Less than 1000
        }
        response = self.client.post(
            '/pos/complete-sale/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        data = response.json()
        self.assertFalse(data['success'])
        self.assertIn('less than total', data['message'])

    def test_pos_return_restocks_inventory(self):
        self.client.login(username='cashier', password='password123')
        # Create a sale first
        sale = POSSale.objects.create(
            cashier=self.staff_user,
            subtotal=Decimal('2000.00'),
            total=Decimal('2000.00'),
            cash_received=Decimal('2000.00'),
            change_amount=Decimal('0.00'),
            status='completed'
        )
        sale_item = POSSaleItem.objects.create(
            sale=sale,
            product=self.product,
            product_name_snapshot=self.product.name,
            unit_price=Decimal('1000.00'),
            quantity=2,
            line_total=Decimal('2000.00')
        )
        self.product.stock = 8
        self.product.save()

        # Perform return of 1 item
        response = self.client.post('/pos/process-return/', {
            'receipt_number': sale.receipt_number,
            'reason': 'Customer changed mind',
            'items_json': json.dumps([{'sale_item_id': sale_item.id, 'quantity': 1}])
        })

        self.assertEqual(response.status_code, 302)

        # Check returned quantity & stock restored (8 + 1 = 9)
        sale_item.refresh_from_db()
        self.assertEqual(sale_item.returned_quantity, 1)

        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 9)
