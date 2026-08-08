"""
KenaKata — Seed Data Management Command
Populates the database with realistic Bangladesh-oriented demo data.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta
import random


class Command(BaseCommand):
    help = 'Seed KenaKata with Bangladesh-focused demo data'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Seeding KenaKata demo data...'))
        self._create_demo_users()
        self._create_brands()
        self._create_categories()
        self._create_products()
        self._create_coupons()
        self._create_banners()
        self._create_pos_demo_data()
        self.stdout.write(self.style.SUCCESS('Demo data and demo accounts seeded successfully!'))
        self.stdout.write(self.style.SUCCESS('  Admin: admin (Use createsuperuser or set DJANGO_SUPERUSER_PASSWORD)'))
        self.stdout.write(self.style.SUCCESS('  Staff: staff'))
        self.stdout.write(self.style.SUCCESS('  User:  customer'))

    def _create_demo_users(self):
        from django.contrib.auth.models import User
        from accounts.models import UserProfile
        import os
        import secrets

        # 1. Admin / Superuser
        admin_user, admin_created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@kenakata.com',
                'first_name': 'Admin',
                'last_name': 'KenaKata',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if admin_created:
            admin_pwd = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
            if not admin_pwd:
                admin_pwd = secrets.token_urlsafe(16)
                self.stdout.write(self.style.WARNING(f"  [!] Admin user generated with temporary password: {admin_pwd}"))
            admin_user.set_password(admin_pwd)
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.email = 'admin@kenakata.com'
            admin_user.save()
            UserProfile.objects.get_or_create(user=admin_user, defaults={'mobile': '01700000001', 'division': 'dhaka'})

        # 2. Staff / POS Cashier
        staff_user, staff_created = User.objects.get_or_create(
            username='staff',
            defaults={
                'email': 'staff@kenakata.com',
                'first_name': 'Staff',
                'last_name': 'Member',
                'is_staff': True,
                'is_superuser': False,
            }
        )
        if staff_created:
            staff_pwd = os.environ.get('DEMO_STAFF_PASSWORD', 'staff1234')
            staff_user.set_password(staff_pwd)
            staff_user.is_staff = True
            staff_user.email = 'staff@kenakata.com'
            staff_user.save()
            UserProfile.objects.get_or_create(user=staff_user, defaults={'mobile': '01700000002', 'division': 'dhaka'})
        UserProfile.objects.get_or_create(user=staff_user, defaults={'mobile': '01700000002', 'division': 'dhaka'})

        # 3. Regular Customer
        customer_user, _ = User.objects.get_or_create(
            username='customer',
            defaults={
                'email': 'customer@kenakata.com',
                'first_name': 'Demo',
                'last_name': 'Customer',
                'is_staff': False,
                'is_superuser': False,
            }
        )
        customer_user.set_password('customer1234')
        customer_user.email = 'customer@kenakata.com'
        customer_user.save()
        UserProfile.objects.get_or_create(user=customer_user, defaults={'mobile': '01700000003', 'division': 'dhaka'})
        self.stdout.write('  [+] 3 Demo users initialized (admin, staff, customer)')

    def _create_brands(self):
        from catalog.models import Brand
        brands_data = [
            'Samsung', 'Apple', 'Xiaomi', 'Realme', 'OnePlus',
            'Sony', 'LG', 'Walton', 'Symphony', 'Anker',
            'JBL', 'Baseus', 'RFL', 'Pran', 'Partex',
            'Apex', 'Fortis', 'Bata', 'Arong', 'Aarong',
        ]
        for name in brands_data:
            Brand.objects.get_or_create(name=name, defaults={'is_active': True})
        self.stdout.write(f'  [+] {len(brands_data)} brands created')

    def _create_categories(self):
        from catalog.models import Category
        cats = [
            {'name': 'Electronics', 'icon': 'bi-cpu', 'order': 1},
            {'name': 'Men\'s Fashion', 'icon': 'bi-person-standing', 'order': 2},
            {'name': 'Women\'s Fashion', 'icon': 'bi-bag-heart', 'order': 3},
            {'name': 'Home & Living', 'icon': 'bi-house-heart', 'order': 4},
            {'name': 'Beauty & Personal Care', 'icon': 'bi-stars', 'order': 5},
            {'name': 'Groceries', 'icon': 'bi-cart3', 'order': 6},
            {'name': 'Books & Stationery', 'icon': 'bi-book', 'order': 7},
            {'name': 'Sports & Lifestyle', 'icon': 'bi-trophy', 'order': 8},
            {'name': 'Mobile Accessories', 'icon': 'bi-phone', 'order': 9},
            {'name': 'Kitchen & Appliances', 'icon': 'bi-egg-fried', 'order': 10},
        ]
        category_objs = {}
        for cat_data in cats:
            cat, _ = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={'icon': cat_data['icon'], 'order': cat_data['order'], 'is_active': True}
            )
            category_objs[cat_data['name']] = cat

        # Subcategories
        subcats = [
            ('Electronics', [('Smartphones', 'bi-phone'), ('Laptops', 'bi-laptop'), ('Headphones', 'bi-headphones'), ('Smart Watches', 'bi-watch'), ('Power Banks', 'bi-battery-charging'), ('Bluetooth Speakers', 'bi-speaker')]),
            ("Men's Fashion", [('Panjabi', 'bi-shirt'), ('Shirts', 'bi-shirt'), ('T-Shirts', 'bi-person'), ('Jeans', 'bi-person'), ('Shoes', 'bi-boot'), ('Watches', 'bi-watch')]),
            ("Women's Fashion", [('Saree', 'bi-bag-heart'), ('Salwar Kameez', 'bi-bag-heart'), ('Kurti', 'bi-bag-heart'), ('Hijab', 'bi-bag-heart'), ('Bags', 'bi-handbag'), ('Jewellery', 'bi-gem')]),
            ('Sports & Lifestyle', [('Cricket Equipment', 'bi-trophy'), ('Football', 'bi-circle'), ('Fitness Products', 'bi-bicycle'), ('Bicycles', 'bi-bicycle')]),
        ]
        for parent_name, children in subcats:
            parent = category_objs.get(parent_name)
            if parent:
                for child_name, icon in children:
                    Category.objects.get_or_create(
                        name=child_name,
                        parent=parent,
                        defaults={'icon': icon, 'is_active': True}
                    )
        self.stdout.write(f'  [+] Categories and subcategories created')

    def _create_products(self):
        from catalog.models import Product, Category, Brand, ProductSpecification
        
        flash_end = timezone.now() + timedelta(hours=6)

        products_data = [
            # Electronics
            {
                'name': 'Samsung Galaxy A55 5G',
                'category': 'Smartphones',
                'brand': 'Samsung',
                'regular_price': 54999,
                'discount_price': 48999,
                'stock': 25,
                'featured': True,
                'flash_sale': True,
                'trending': True,
                'best_seller': True,
                'rating': 4.7,
                'reviews': 124,
                'sold': 450,
                'short_desc': '6.6" Super AMOLED, 50MP Camera, 5000mAh Battery, 5G Ready',
                'desc': 'The Samsung Galaxy A55 5G features a stunning 6.6-inch Super AMOLED display with 120Hz refresh rate. Powered by Exynos 1480 processor with 8GB RAM and 256GB storage. The 50MP main camera with OIS delivers stunning photos even in low light.',
                'specs': [('Display', '6.6" Super AMOLED, 120Hz'), ('Processor', 'Exynos 1480'), ('RAM', '8GB'), ('Storage', '256GB'), ('Camera', '50MP + 12MP + 5MP'), ('Battery', '5000mAh, 45W fast charge'), ('OS', 'Android 14'), ('5G', 'Yes')]
            },
            {
                'name': 'Xiaomi Redmi Note 13 Pro',
                'category': 'Smartphones',
                'brand': 'Xiaomi',
                'regular_price': 34999,
                'discount_price': 28999,
                'stock': 40,
                'featured': True,
                'flash_sale': True,
                'trending': True,
                'rating': 4.5,
                'reviews': 89,
                'sold': 320,
                'short_desc': '200MP Camera, 5000mAh, 67W Turbo Charge, AMOLED Display',
                'desc': 'Xiaomi Redmi Note 13 Pro with industry-leading 200MP camera system. Features 6.67-inch 1.5K AMOLED curved display, powerful MediaTek Dimensity 7200-Ultra processor, and 67W turbo charging that fills from 0 to 100% in just 46 minutes.',
                'specs': [('Display', '6.67" AMOLED, 120Hz'), ('Processor', 'Dimensity 7200-Ultra'), ('RAM', '8GB'), ('Storage', '256GB'), ('Camera', '200MP + 8MP + 2MP'), ('Battery', '5000mAh, 67W fast charge')]
            },
            {
                'name': 'Walton Primo RX8 Mini',
                'category': 'Smartphones',
                'brand': 'Walton',
                'regular_price': 14999,
                'discount_price': 12499,
                'stock': 60,
                'new_arrival': True,
                'rating': 4.1,
                'reviews': 45,
                'sold': 180,
                'short_desc': 'Made in Bangladesh | 6.5" HD+, 5000mAh, 4GB RAM',
                'desc': 'Walton Primo RX8 Mini — proudly made in Bangladesh. Great value smartphone with 6.5-inch HD+ display, 5000mAh battery, and quad-camera setup.',
                'specs': [('Display', '6.5" HD+'), ('RAM', '4GB'), ('Storage', '64GB'), ('Battery', '5000mAh'), ('OS', 'Android 13')]
            },
            {
                'name': 'Wireless Earbuds Pro (TWS)',
                'category': 'Headphones',
                'brand': 'Baseus',
                'regular_price': 2499,
                'discount_price': 1799,
                'stock': 80,
                'featured': True,
                'flash_sale': True,
                'trending': True,
                'new_arrival': True,
                'best_seller': True,
                'rating': 4.6,
                'reviews': 156,
                'sold': 892,
                'short_desc': 'Active Noise Cancellation, 30hr Battery, BT 5.3',
                'desc': 'Premium true wireless earbuds with active noise cancellation. Enjoy up to 30 hours of total playback time with the charging case. Features Bluetooth 5.3 for stable connection and low latency gaming mode.',
                'specs': [('Driver', '13mm Dynamic'), ('ANC', 'Active Noise Cancellation'), ('Battery', '7hr + 23hr case'), ('Bluetooth', '5.3'), ('Charging', 'USB-C + Wireless')]
            },
            {
                'name': 'Anker PowerBank 20000mAh',
                'category': 'Power Banks',
                'brand': 'Anker',
                'regular_price': 3999,
                'discount_price': 2999,
                'stock': 45,
                'featured': True,
                'flash_sale': True,
                'best_seller': True,
                'rating': 4.8,
                'reviews': 203,
                'sold': 1250,
                'short_desc': '20000mAh, 22.5W Fast Charge, 3 Outputs, PowerIQ 3.0',
                'desc': 'Anker 523 Power Bank with massive 20000mAh capacity. Features 22.5W fast charging, three output ports (2x USB-A + 1x USB-C), and Anker\'s PowerIQ 3.0 technology for intelligent charging.',
                'specs': [('Capacity', '20000mAh'), ('Output', '22.5W Max'), ('Ports', '2x USB-A + 1x USB-C'), ('Input', '18W USB-C'), ('Technology', 'PowerIQ 3.0')]
            },
            {
                'name': 'JBL Bluetooth Speaker Flip 6',
                'category': 'Bluetooth Speakers',
                'brand': 'JBL',
                'regular_price': 12999,
                'discount_price': 9999,
                'stock': 30,
                'featured': True,
                'trending': True,
                'rating': 4.7,
                'reviews': 87,
                'sold': 340,
                'short_desc': 'IP67 Waterproof, 12hr Battery, PartyBoost, Powerful Bass',
                'desc': 'JBL Flip 6 delivers bold JBL Original Pro Sound with powerful bass from its two-way speaker system. IP67 waterproof and dustproof, 12 hours of playtime, and PartyBoost to connect multiple speakers.',
                'specs': [('Output Power', '30W'), ('Battery', '12 hours'), ('Waterproof', 'IP67'), ('Connectivity', 'Bluetooth 5.1'), ('Weight', '550g')]
            },
            {
                'name': 'Smart Watch HK9 Pro',
                'category': 'Smart Watches',
                'brand': 'Baseus',
                'regular_price': 4999,
                'discount_price': 2999,
                'stock': 55,
                'featured': True,
                'flash_sale': True,
                'trending': True,
                'rating': 4.3,
                'reviews': 72,
                'sold': 560,
                'short_desc': 'AMOLED, Health Monitor, GPS, 7-day Battery',
                'desc': 'Smart watch with 2.02-inch HD AMOLED display. Tracks heart rate, SpO2, sleep, and stress. Built-in GPS, 100+ sport modes, and up to 7 days battery life. IP68 water resistant.',
                'specs': [('Display', '2.02" AMOLED'), ('Battery', '7 days'), ('Health', 'HR, SpO2, Sleep'), ('GPS', 'Yes'), ('Water', 'IP68')]
            },
            {
                'name': 'Gaming Mouse Logitech G102',
                'category': 'Mobile Accessories',
                'brand': 'LG',
                'regular_price': 2999,
                'discount_price': 1999,
                'stock': 35,
                'trending': True,
                'best_seller': True,
                'rating': 4.5,
                'reviews': 98,
                'sold': 420,
                'short_desc': '8000 DPI, 6 buttons, RGB, Lightweight 85g',
                'desc': 'Logitech G102 LIGHTSYNC gaming mouse with 8000 DPI sensor, customizable RGB, 6 programmable buttons, and weighing only 85g for lightning-fast gameplay.',
                'specs': [('DPI', '200-8000'), ('Buttons', '6 programmable'), ('Weight', '85g'), ('Cable', '1.8m braided'), ('Sensor', 'Mercury Optical')]
            },
            # Men's Fashion
            {
                'name': 'Premium Cotton Panjabi — Eid Special',
                'category': 'Panjabi',
                'brand': 'Arong',
                'regular_price': 1999,
                'discount_price': 1499,
                'stock': 100,
                'featured': True,
                'trending': True,
                'new_arrival': True,
                'rating': 4.4,
                'reviews': 56,
                'sold': 280,
                'short_desc': '100% Cotton, Embroidered, Available in M/L/XL/XXL',
                'desc': 'Premium quality cotton Panjabi with beautiful embroidery work. Perfect for Eid celebrations, weddings, and special occasions. Made from 100% pure cotton for maximum comfort in Bangladesh\'s climate.',
                'specs': [('Material', '100% Cotton'), ('Sizes', 'M, L, XL, XXL'), ('Color', 'White, Cream, Blue'), ('Occasion', 'Eid, Wedding, Festival'), ('Care', 'Machine Washable')]
            },
            {
                'name': 'Men\'s Casual Slim Fit Shirt',
                'category': 'Shirts',
                'brand': 'Apex',
                'regular_price': 899,
                'discount_price': 699,
                'stock': 150,
                'new_arrival': True,
                'rating': 4.2,
                'reviews': 34,
                'sold': 195,
                'short_desc': 'Cotton Blend, Slim Fit, 5 Colors Available',
                'desc': 'Stylish slim fit casual shirt for men. Made from premium cotton blend fabric. Available in 5 attractive colors. Perfect for office, casual outings, or smart casual occasions.',
                'specs': [('Material', 'Cotton Blend 60/40'), ('Fit', 'Slim Fit'), ('Sizes', 'S, M, L, XL, XXL'), ('Colors', 5)]
            },
            {
                'name': 'Classic Cotton T-Shirt Pack (3pcs)',
                'category': 'T-Shirts',
                'brand': 'Fortis',
                'regular_price': 1199,
                'discount_price': 849,
                'stock': 200,
                'best_seller': True,
                'trending': True,
                'rating': 4.3,
                'reviews': 78,
                'sold': 650,
                'short_desc': 'Pack of 3, 100% Cotton, Crew Neck, Multiple Colors',
                'desc': '3-pack of classic cotton t-shirts. Made from 100% combed cotton for superior softness and comfort. Crew neck design, regular fit. Available in assorted colors.',
                'specs': [('Quantity', '3 pieces'), ('Material', '100% Combed Cotton'), ('Fit', 'Regular'), ('Neck', 'Crew Neck')]
            },
            # Women's Fashion
            {
                'name': 'Handloom Cotton Saree — Traditional',
                'category': 'Saree',
                'brand': 'Arong',
                'regular_price': 3999,
                'discount_price': 2999,
                'stock': 40,
                'featured': True,
                'new_arrival': True,
                'rating': 4.8,
                'reviews': 67,
                'sold': 145,
                'short_desc': 'Authentic Handloom, 5.5m + Blouse Piece, Jamdani Inspired',
                'desc': 'Beautiful handloom cotton saree inspired by traditional Jamdani weaving. Features intricate patterns woven by skilled artisans. Includes matching blouse piece. 5.5 meters length. Perfect for weddings, Eid, Pohela Boishakh.',
                'specs': [('Length', '5.5m + Blouse Piece'), ('Material', 'Handloom Cotton'), ('Occasion', 'Festival, Wedding, Eid'), ('Wash', 'Dry Clean Recommended')]
            },
            {
                'name': 'Salwar Kameez Set — Summer Collection',
                'category': 'Salwar Kameez',
                'brand': 'Arong',
                'regular_price': 2499,
                'discount_price': 1799,
                'stock': 55,
                'new_arrival': True,
                'trending': True,
                'rating': 4.5,
                'reviews': 43,
                'sold': 220,
                'short_desc': 'Cotton Kameez + Salwar + Dupatta, 4 Colors',
                'desc': 'Complete 3-piece summer salwar kameez set. Lightweight cotton fabric ideal for Bangladesh\'s warm climate. Includes kameez, salwar, and matching dupatta. Machine washable.',
                'specs': [('Pieces', '3 (Kameez + Salwar + Dupatta)'), ('Material', 'Cotton'), ('Sizes', 'S, M, L, XL, XXL'), ('Colors', '4 available')]
            },
            {
                'name': 'Women\'s Handbag — Premium PU Leather',
                'category': 'Bags',
                'brand': 'Apex',
                'regular_price': 2999,
                'discount_price': 1999,
                'stock': 35,
                'featured': True,
                'trending': True,
                'rating': 4.4,
                'reviews': 55,
                'sold': 190,
                'short_desc': 'PU Leather, Multiple Compartments, Stylish Design',
                'desc': 'Premium PU leather handbag with elegant design. Features multiple compartments for organization, zipper closure, and detachable shoulder strap. Perfect for daily use, office, or going out.',
                'specs': [('Material', 'PU Leather'), ('Compartments', '3 main + 2 small'), ('Strap', 'Detachable'), ('Dimensions', '35x26x12 cm')]
            },
            # Home & Living
            {
                'name': 'Miyako Rice Cooker 1.8L',
                'category': 'Kitchen & Appliances',
                'brand': 'RFL',
                'regular_price': 3499,
                'discount_price': 2699,
                'stock': 45,
                'featured': True,
                'best_seller': True,
                'rating': 4.6,
                'reviews': 112,
                'sold': 480,
                'short_desc': '1.8L Capacity, Auto Cook & Warm, 700W, Safety Valve',
                'desc': 'Miyako rice cooker with 1.8L capacity, perfect for family of 4-6. Features automatic cooking and warming function, stainless steel inner pot, and steam vent safety valve.',
                'specs': [('Capacity', '1.8 Liter'), ('Power', '700W'), ('Voltage', '220V'), ('Functions', 'Cook & Warm'), ('Inner Pot', 'Non-stick coated')]
            },
            {
                'name': 'Electric Kettle 1.8L Stainless Steel',
                'category': 'Kitchen & Appliances',
                'brand': 'RFL',
                'regular_price': 1999,
                'discount_price': 1499,
                'stock': 60,
                'best_seller': True,
                'new_arrival': True,
                'rating': 4.5,
                'reviews': 88,
                'sold': 360,
                'short_desc': '1500W Fast Boil, Auto-Off, LED Indicator, Cordless',
                'desc': 'Stainless steel electric kettle that boils 1.8L of water in under 3 minutes. Features automatic shut-off when water boils, boil-dry protection, LED indicator, and 360° cordless base.',
                'specs': [('Capacity', '1.8 Liter'), ('Power', '1500W'), ('Material', 'Stainless Steel'), ('Features', 'Auto-off, Boil-dry protection')]
            },
            {
                'name': 'Non-Stick Cookware Set 5-Piece',
                'category': 'Kitchen & Appliances',
                'brand': 'Partex',
                'regular_price': 5999,
                'discount_price': 3999,
                'stock': 25,
                'featured': True,
                'rating': 4.3,
                'reviews': 64,
                'sold': 175,
                'short_desc': '5-piece set, Granite coating, Gas + Induction compatible',
                'desc': '5-piece granite coated non-stick cookware set including 2 frying pans, 1 sauce pan, 1 deep pan, and lids. Compatible with gas stove and induction cooktop. PFOA-free coating.',
                'specs': [('Pieces', '5 (pans + lids)'), ('Coating', 'Granite Non-stick'), ('Compatible', 'Gas + Induction'), ('Material', 'Aluminum')]
            },
            # Groceries & Budget
            {
                'name': 'Pran Basmati Rice 5KG',
                'category': 'Groceries',
                'brand': 'Pran',
                'regular_price': 799,
                'discount_price': 649,
                'stock': 500,
                'best_seller': True,
                'trending': True,
                'rating': 4.4,
                'reviews': 234,
                'sold': 2100,
                'short_desc': 'Premium Long Grain, Aromatic, 5KG Pack',
                'desc': 'Pran Premium Basmati Rice — long grain, naturally aromatic, and aged for superior taste. 5KG family pack. Perfect for biriyani, pulao, and everyday cooking.',
                'specs': [('Weight', '5 KG'), ('Type', 'Long Grain Basmati'), ('Origin', 'Bangladesh'), ('Shelf Life', '12 months')]
            },
            {
                'name': 'Pran Mustard Oil 1L',
                'category': 'Groceries',
                'brand': 'Pran',
                'regular_price': 299,
                'discount_price': 249,
                'stock': 800,
                'best_seller': True,
                'rating': 4.5,
                'reviews': 178,
                'sold': 3200,
                'short_desc': 'Pure Mustard Oil, Cold Pressed, 1 Liter',
                'desc': 'Pure cold-pressed mustard oil. Rich in Omega-3 fatty acids and naturally flavored. Perfect for cooking and traditional recipes.',
                'specs': [('Volume', '1 Liter'), ('Type', 'Cold Pressed'), ('Fat', 'Omega-3 rich')]
            },
            # Sports & Lifestyle
            {
                'name': 'Cricket Bat — Kashmir Willow Grade A',
                'category': 'Cricket Equipment',
                'brand': 'Apex',
                'regular_price': 4999,
                'discount_price': 3499,
                'stock': 30,
                'featured': True,
                'trending': True,
                'rating': 4.6,
                'reviews': 45,
                'sold': 120,
                'short_desc': 'Kashmir Willow, Full Size, Professional Grade, Free Grip',
                'desc': 'Professional grade Kashmir Willow cricket bat. Full size (33.5 inches) with premium rubber grip. Ideal for club and recreational cricket. Pre-knocked and ready to play.',
                'specs': [('Material', 'Kashmir Willow Grade A'), ('Size', 'Full Size - 33.5 inches'), ('Weight', '1.1-1.2 kg'), ('Includes', 'Free grip + Cover')]
            },
            # Beauty & Personal Care
            {
                'name': 'Fair & Lovely Glow Cream 80g',
                'category': 'Beauty & Personal Care',
                'brand': 'LG',
                'regular_price': 299,
                'discount_price': 249,
                'stock': 300,
                'best_seller': True,
                'rating': 4.2,
                'reviews': 145,
                'sold': 1800,
                'short_desc': 'SPF 15, Vitamin B3+C+E, 12hr Moisture',
                'desc': 'Advanced multi-vitamin cream with SPF 15 sun protection. Formulated with Vitamins B3, C and E for radiant, glowing skin. Provides 12-hour moisture lock.',
                'specs': [('Weight', '80g'), ('SPF', '15'), ('Vitamins', 'B3, C, E'), ('Suitable', 'All skin types')]
            },
            # Budget deals
            {
                'name': 'USB-C Fast Charging Cable 2m',
                'category': 'Mobile Accessories',
                'brand': 'Baseus',
                'regular_price': 699,
                'discount_price': 449,
                'stock': 200,
                'best_seller': True,
                'trending': True,
                'rating': 4.4,
                'reviews': 189,
                'sold': 2400,
                'short_desc': '100W Fast Charge, Nylon Braided, 2 Meter',
                'desc': 'Baseus 100W USB-C to USB-C fast charging cable. Nylon braided for durability, 2 meter length for convenience. Compatible with all USB-C devices.',
                'specs': [('Length', '2 Meter'), ('Power', '100W'), ('Type', 'USB-C to USB-C'), ('Material', 'Nylon Braided')]
            },
            {
                'name': 'Study Table Lamp with USB Charging',
                'category': 'Home & Living',
                'brand': 'RFL',
                'regular_price': 1299,
                'discount_price': 899,
                'stock': 75,
                'new_arrival': True,
                'rating': 4.3,
                'reviews': 67,
                'sold': 290,
                'short_desc': 'LED, Touch Control, USB Charging Port, 3 Color Modes',
                'desc': 'LED desk lamp with touch control, 3 color temperature modes (warm/natural/cool), and 5 brightness levels. Includes USB charging port. Perfect for students and home office.',
                'specs': [('Type', 'LED'), ('Control', 'Touch'), ('Color Modes', '3 (Warm/Natural/Cool)'), ('USB Port', 'Yes, USB-A')]
            },
            {
                'name': 'Backpack 20L — Laptop Compartment',
                'category': 'Sports & Lifestyle',
                'brand': 'Fortis',
                'regular_price': 1999,
                'discount_price': 1299,
                'stock': 90,
                'featured': True,
                'best_seller': True,
                'rating': 4.5,
                'reviews': 93,
                'sold': 410,
                'short_desc': '20L, 15.6" Laptop Compartment, USB Charging Port, Water Resistant',
                'desc': 'Multi-function backpack with dedicated 15.6-inch laptop compartment, external USB charging port, multiple pockets for organization. Made from water-resistant polyester.',
                'specs': [('Capacity', '20 Liter'), ('Laptop', 'Up to 15.6 inches'), ('USB Port', 'External'), ('Material', 'Water-resistant Polyester')]
            },
        ]

        from catalog.models import Category as Cat
        from catalog.models import Brand as Br

        count = 0
        for data in products_data:
            # Get category
            try:
                category = Cat.objects.get(name=data['category'])
            except Cat.DoesNotExist:
                try:
                    category = Cat.objects.get(name=data.get('parent_cat', data['category']))
                except Cat.DoesNotExist:
                    category = Cat.objects.first()

            # Get brand
            brand = None
            if data.get('brand'):
                try:
                    brand = Br.objects.get(name=data['brand'])
                except Br.DoesNotExist:
                    pass

            product, created = Product.objects.get_or_create(
                name=data['name'],
                defaults={
                    'category': category,
                    'brand': brand,
                    'regular_price': Decimal(str(data['regular_price'])),
                    'discount_price': Decimal(str(data['discount_price'])) if data.get('discount_price') else None,
                    'stock': data.get('stock', 50),
                    'featured': data.get('featured', False),
                    'flash_sale': data.get('flash_sale', False),
                    'flash_sale_end': flash_end if data.get('flash_sale') else None,
                    'trending': data.get('trending', False),
                    'new_arrival': data.get('new_arrival', False),
                    'best_seller': data.get('best_seller', False),
                    'average_rating': Decimal(str(data.get('rating', 0))),
                    'review_count': data.get('reviews', 0),
                    'active': True,
                }
            )

            # Assign high-res CDN product image URL
            if not product.image_url:
                product.image_url = product.get_main_image_url()
                product.save(update_fields=['image_url'])

            if created:
                # Create specs
                for i, (key, val) in enumerate(data.get('specs', [])):
                    ProductSpecification.objects.create(product=product, key=key, value=str(val), order=i)
                count += 1

        self.stdout.write(f'  [+] {count} products created (skipped existing)')

    def _create_coupons(self):
        from cart.models import Coupon
        coupons = [
            {
                'code': 'HACKATHON10',
                'description': '10% off — Hackathon Demo Coupon',
                'discount_type': 'percentage',
                'discount_value': Decimal('10'),
                'min_order_amount': Decimal('500'),
                'max_discount_amount': Decimal('1000'),
            },
            {
                'code': 'WELCOME100',
                'description': '৳100 off for new users',
                'discount_type': 'fixed',
                'discount_value': Decimal('100'),
                'min_order_amount': Decimal('1000'),
            },
            {
                'code': 'BDDEAL',
                'description': '15% Bangladesh Deal',
                'discount_type': 'percentage',
                'discount_value': Decimal('15'),
                'min_order_amount': Decimal('2000'),
                'max_discount_amount': Decimal('500'),
            },
            {
                'code': 'EID2026',
                'description': '20% Eid Special Discount',
                'discount_type': 'percentage',
                'discount_value': Decimal('20'),
                'min_order_amount': Decimal('3000'),
                'max_discount_amount': Decimal('2000'),
            },
        ]
        for coup_data in coupons:
            Coupon.objects.get_or_create(
                code=coup_data['code'],
                defaults={**coup_data, 'is_active': True, 'expiry_date': timezone.now() + timedelta(days=365)}
            )
        self.stdout.write(f'  [+] {len(coupons)} coupons created')

    def _create_banners(self):
        from catalog.models import Banner
        banners = [
            {
                'title': 'Mega Electronics Sale',
                'subtitle': 'Up to 40% Off on Smartphones, Laptops & More',
                'cta_text': 'Shop Now',
                'cta_url': '/shop/?category=electronics',
                'bg_color': '#1a6b3c',
                'banner_type': 'hero',
                'order': 1,
            },
            {
                'title': 'Eid Fashion Festival',
                'subtitle': 'Premium Panjabi, Saree & Kurti Collection',
                'cta_text': 'Explore Collection',
                'cta_url': '/shop/',
                'bg_color': '#7c3aed',
                'banner_type': 'hero',
                'order': 2,
            },
            {
                'title': 'Friday Mega Deals',
                'subtitle': 'Special discounts every Friday — Don\'t miss out!',
                'cta_text': 'View Deals',
                'cta_url': '/shop/?on_sale=1',
                'bg_color': '#dc2626',
                'banner_type': 'hero',
                'order': 3,
            },
            {
                'title': 'Tech Week Bangladesh',
                'subtitle': 'Upgrade your tech this season',
                'cta_text': 'Shop Tech',
                'cta_url': '/search/?q=electronics',
                'bg_color': '#0f3460',
                'banner_type': 'promotional',
                'order': 1,
            },
        ]
        for ban_data in banners:
            Banner.objects.get_or_create(
                title=ban_data['title'],
                defaults={**ban_data, 'is_active': True}
            )
        self.stdout.write(f'  [+] {len(banners)} banners created')

    def _create_pos_demo_data(self):
        from pos.models import StoreSettings, POSCustomer, POSSale, POSSaleItem, InventoryMovement
        from catalog.models import Product
        from django.contrib.auth.models import User

        # Store Settings
        StoreSettings.get_settings()

        # POS Customers
        c1, _ = POSCustomer.objects.get_or_create(name='Rahim Uddin', mobile='01711223344', defaults={'email': 'rahim@example.com', 'address': 'Gulshan-1, Dhaka'})
        c2, _ = POSCustomer.objects.get_or_create(name='Fatema Begum', mobile='01899887766', defaults={'email': 'fatema@example.com', 'address': 'Dhanmondi 27, Dhaka'})
        c3, _ = POSCustomer.objects.get_or_create(name='Tanvir Ahmed', mobile='01955443322', defaults={'email': 'tanvir@example.com', 'address': 'Uttara Sector 4, Dhaka'})

        admin_user = User.objects.filter(is_staff=True).first()

        # Create demo sales
        prods = list(Product.objects.filter(active=True)[:5])
        if prods and admin_user:
            p1 = prods[0]
            p2 = prods[1] if len(prods) > 1 else prods[0]

            if not POSSale.objects.exists():
                sale = POSSale.objects.create(
                    cashier=admin_user,
                    customer=c1,
                    subtotal=p1.selling_price * 2 + p2.selling_price,
                    discount_type='none',
                    total=p1.selling_price * 2 + p2.selling_price,
                    cash_received=p1.selling_price * 2 + p2.selling_price + 500,
                    change_amount=Decimal('500.00'),
                    payment_method='CASH',
                    payment_status='PAID',
                    status='completed'
                )
                POSSaleItem.objects.create(
                    sale=sale,
                    product=p1,
                    product_name_snapshot=p1.name,
                    sku_snapshot=p1.sku,
                    unit_price=p1.selling_price,
                    quantity=2,
                    line_total=p1.selling_price * 2
                )
                POSSaleItem.objects.create(
                    sale=sale,
                    product=p2,
                    product_name_snapshot=p2.name,
                    sku_snapshot=p2.sku,
                    unit_price=p2.selling_price,
                    quantity=1,
                    line_total=p2.selling_price
                )
        self.stdout.write('  [+] POS store settings, customers, and initial sales populated')
