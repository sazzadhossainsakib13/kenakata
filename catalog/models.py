from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.contrib.auth.models import User
from decimal import Decimal
import uuid


class Category(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='children')
    icon = models.CharField(max_length=100, blank=True, help_text="Bootstrap icon class e.g. bi-phone")
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    image_url = models.URLField(max_length=1000, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['order', 'name']

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name

    def get_absolute_url(self):
        return reverse('catalog:category_detail', kwargs={'slug': self.slug})

    def get_image_url(self):
        if self.image:
            try:
                return self.image.url
            except Exception:
                pass
        if self.image_url:
            return self.image_url
        return '/static/images/placeholder.svg'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Brand(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    logo = models.ImageField(upload_to='brands/', blank=True, null=True)
    logo_url = models.URLField(max_length=1000, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def get_logo_url(self):
        if self.logo:
            try:
                return self.logo.url
            except Exception:
                pass
        if self.logo_url:
            return self.logo_url
        return '/static/images/placeholder.svg'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    name = models.CharField(max_length=500)
    slug = models.SlugField(max_length=500, unique=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    sku = models.CharField(max_length=100, unique=True, blank=True)
    barcode = models.CharField(max_length=100, unique=True, null=True, blank=True, db_index=True)
    short_description = models.TextField(max_length=500, blank=True)
    description = models.TextField(blank=True)
    regular_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    image_url = models.URLField(max_length=1000, blank=True)
    # Status flags
    featured = models.BooleanField(default=False)
    flash_sale = models.BooleanField(default=False)
    flash_sale_end = models.DateTimeField(null=True, blank=True)
    trending = models.BooleanField(default=False)
    new_arrival = models.BooleanField(default=False)
    best_seller = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    # Aggregated stats
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=Decimal('0.00'))
    review_count = models.PositiveIntegerField(default=0)
    sold_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('catalog:product_detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        if not self.sku:
            self.sku = f"KK-{uuid.uuid4().hex[:8].upper()}"
        if not self.barcode:
            import random
            self.barcode = f"894{random.randint(100000000, 999999999)}"
        super().save(*args, **kwargs)

    @property
    def selling_price(self):
        if self.discount_price:
            return self.discount_price
        return self.regular_price

    @property
    def discount_percentage(self):
        if self.discount_price and self.regular_price > 0:
            discount = ((self.regular_price - self.discount_price) / self.regular_price) * 100
            return int(discount)
        return 0

    @property
    def is_in_stock(self):
        return self.stock > 0

    @property
    def is_on_sale(self):
        return bool(self.discount_price and self.discount_price < self.regular_price)

    def get_main_image_url(self):
        if self.image:
            try:
                return self.image.url
            except Exception:
                pass
        if self.image_url:
            return self.image_url
        img_obj = self.images.first()
        if img_obj and img_obj.image:
            try:
                return img_obj.image.url
            except Exception:
                pass
        
        name_lower = (self.name or '').lower()
        cat_lower = (self.category.name if self.category else '').lower()
        
        if 'phone' in name_lower or 'galaxy' in name_lower or 'redmi' in name_lower or 'smartphones' in cat_lower or 'mobile' in cat_lower:
            return 'https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=600&auto=format&fit=crop&q=80'
        elif 'earbud' in name_lower or 'headphone' in name_lower or 'audio' in cat_lower or 'tws' in name_lower or 'speaker' in name_lower:
            return 'https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=600&auto=format&fit=crop&q=80'
        elif 'watch' in name_lower:
            return 'https://images.unsplash.com/photo-1524805444758-089113d48a6d?w=600&auto=format&fit=crop&q=80'
        elif 'laptop' in name_lower or 'macbook' in name_lower or 'computer' in cat_lower:
            return 'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=600&auto=format&fit=crop&q=80'
        elif 'panjabi' in name_lower or 'shirt' in name_lower or "men's" in cat_lower or 'polo' in name_lower:
            return 'https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?w=600&auto=format&fit=crop&q=80'
        elif 'saree' in name_lower or 'kurti' in name_lower or "women's" in cat_lower or 'dress' in name_lower or 'hijab' in name_lower:
            return 'https://images.unsplash.com/photo-1610030469983-98e550d6193c?w=600&auto=format&fit=crop&q=80'
        elif 'tea' in name_lower or 'oil' in name_lower or 'rice' in name_lower or 'grocery' in cat_lower or 'groceries' in cat_lower:
            return 'https://images.unsplash.com/photo-1576092768241-dec231879fc3?w=600&auto=format&fit=crop&q=80'
        elif 'shoe' in name_lower or 'sneaker' in name_lower or 'bata' in name_lower or 'apex' in name_lower:
            return 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600&auto=format&fit=crop&q=80'
        elif 'cricket' in name_lower or 'football' in name_lower or 'sport' in cat_lower:
            return 'https://images.unsplash.com/photo-1531415074968-036ba1b575da?w=600&auto=format&fit=crop&q=80'
        
        return '/static/images/placeholder.svg'


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/')
    alt_text = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.product.name} - Image {self.order}"


class ProductSpecification(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='specifications')
    key = models.CharField(max_length=200)
    value = models.CharField(max_length=500)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.product.name}: {self.key}"


class RecentlyViewed(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='recently_viewed')
    session_key = models.CharField(max_length=40, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-viewed_at']
        unique_together = [['user', 'product'], ['session_key', 'product']]

    def __str__(self):
        return f"Recently viewed: {self.product.name}"


class Banner(models.Model):
    BANNER_TYPES = [
        ('hero', 'Hero Slider'),
        ('promotional', 'Promotional'),
        ('category', 'Category'),
    ]
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=300, blank=True)
    cta_text = models.CharField(max_length=100, blank=True, default='Shop Now')
    cta_url = models.CharField(max_length=300, blank=True, default='/')
    image = models.ImageField(upload_to='banners/', blank=True, null=True)
    image_url = models.URLField(max_length=1000, blank=True)
    bg_color = models.CharField(max_length=20, blank=True, default='#1a6b3c')
    text_color = models.CharField(max_length=20, blank=True, default='#ffffff')
    banner_type = models.CharField(max_length=20, choices=BANNER_TYPES, default='hero')
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title

    def get_image_url(self):
        if self.image:
            try:
                return self.image.url
            except Exception:
                pass
        if self.image_url:
            return self.image_url
        return 'https://images.unsplash.com/photo-1607082348824-0a96f2a4b9da?w=1600&auto=format&fit=crop&q=80'

