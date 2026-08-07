from django.test import TestCase
from decimal import Decimal
from catalog.models import Category, Product, Brand


class CatalogModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Electronics', icon='bi-cpu')
        self.brand = Brand.objects.create(name='Samsung')
        self.product = Product.objects.create(
            name='Samsung S24 Ultra',
            category=self.category,
            brand=self.brand,
            regular_price=Decimal('100000.00'),
            discount_price=Decimal('80000.00'),
            stock=10,
            active=True
        )

    def test_selling_price_with_discount(self):
        self.assertEqual(self.product.selling_price, Decimal('80000.00'))

    def test_discount_percentage(self):
        self.assertEqual(self.product.discount_percentage, 20)

    def test_selling_price_without_discount(self):
        product2 = Product.objects.create(
            name='Standard Headphones',
            category=self.category,
            regular_price=Decimal('2000.00'),
            stock=5,
            active=True
        )
        self.assertEqual(product2.selling_price, Decimal('2000.00'))
        self.assertEqual(product2.discount_percentage, 0)

    def test_stock_status(self):
        self.assertTrue(self.product.is_in_stock)
        self.product.stock = 0
        self.product.save()
        self.assertFalse(self.product.is_in_stock)


class CatalogViewsTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Gadgets', icon='bi-phone')
        self.product = Product.objects.create(
            name='Smart Watch',
            category=self.category,
            regular_price=Decimal('5000.00'),
            stock=5,
            active=True
        )

    def test_shop_page_loads(self):
        response = self.client.get('/shop/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Smart Watch')

    def test_product_detail_page_loads(self):
        response = self.client.get(f'/shop/product/{self.product.slug}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Smart Watch')
