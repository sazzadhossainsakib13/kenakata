from django.db import models
from django.contrib.auth.models import User


BANGLADESH_DIVISIONS = [
    ('dhaka', 'Dhaka'),
    ('chattogram', 'Chattogram'),
    ('rajshahi', 'Rajshahi'),
    ('khulna', 'Khulna'),
    ('barishal', 'Barishal'),
    ('sylhet', 'Sylhet'),
    ('rangpur', 'Rangpur'),
    ('mymensingh', 'Mymensingh'),
]

ADDRESS_LABELS = [
    ('home', 'Home'),
    ('office', 'Office'),
    ('parents', "Parents' House"),
    ('other', 'Other'),
]


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='profiles/', blank=True, null=True)
    mobile = models.CharField(max_length=15, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], blank=True)
    division = models.CharField(max_length=20, choices=BANGLADESH_DIVISIONS, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Profile: {self.user.get_full_name() or self.user.username}"

    @property
    def display_name(self):
        return self.user.get_full_name() or self.user.username


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    label = models.CharField(max_length=20, choices=ADDRESS_LABELS, default='home')
    recipient_name = models.CharField(max_length=200)
    mobile = models.CharField(max_length=15)
    email = models.EmailField(blank=True)
    division = models.CharField(max_length=20, choices=BANGLADESH_DIVISIONS)
    district = models.CharField(max_length=100)
    upazila = models.CharField(max_length=100, blank=True)
    area = models.CharField(max_length=200, blank=True)
    road = models.CharField(max_length=200, blank=True)
    house = models.CharField(max_length=200, blank=True)
    postal_code = models.CharField(max_length=10, blank=True)
    full_address = models.TextField(blank=True)
    delivery_instructions = models.TextField(blank=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_default', '-created_at']
        verbose_name_plural = 'Addresses'

    def __str__(self):
        return f"{self.recipient_name} — {self.district}, {self.get_division_display()}"

    def get_short_address(self):
        parts = [self.area, self.district, self.get_division_display()]
        return ', '.join([p for p in parts if p])

    def get_full_address_display(self):
        parts = [self.house, self.road, self.area, self.upazila, self.district, self.get_division_display()]
        return ', '.join([p for p in parts if p])

    def save(self, *args, **kwargs):
        if self.is_default:
            Address.objects.filter(user=self.user, is_default=True).update(is_default=False)
        super().save(*args, **kwargs)
