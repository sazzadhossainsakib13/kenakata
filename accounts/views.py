from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils.http import url_has_allowed_host_and_scheme
from django.core.cache import cache
from .models import UserProfile
import re


def validate_bd_mobile(mobile):
    cleaned = re.sub(r'[\s\-\(\)]', '', mobile)
    pattern = r'^(\+880|880|0)?1[3-9]\d{8}$'
    return bool(re.match(pattern, cleaned))


def get_client_ip(request):
    """Retrieve client IP address securely."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip or '127.0.0.1'


MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_SECONDS = 900  # 15 minutes


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')

    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        mobile = request.POST.get('mobile', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        errors = []
        field_errors = {}
        if not first_name:
            errors.append("First name is required.")
            field_errors['first_name'] = "First name is required."
        if not email:
            errors.append("Email is required.")
            field_errors['email'] = "Email is required."
        if not mobile:
            errors.append("Mobile number is required.")
            field_errors['mobile'] = "Mobile number is required."
        elif not validate_bd_mobile(mobile):
            errors.append("Please enter a valid Bangladesh mobile number (01XXXXXXXXX).")
            field_errors['mobile'] = "Please enter a valid Bangladesh mobile number (01XXXXXXXXX)."
        if not password:
            errors.append("Password is required.")
            field_errors['password'] = "Password is required."
        elif len(password) < 8:
            errors.append("Password must be at least 8 characters.")
            field_errors['password'] = "Password must be at least 8 characters."
        if password != confirm_password:
            errors.append("Passwords do not match.")
            field_errors['confirm_password'] = "Passwords do not match."
        if User.objects.filter(email__iexact=email).exists() or User.objects.filter(username__iexact=email).exists():
            errors.append("An account with this email already exists.")
            field_errors['email'] = "An account with this email already exists."

        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'accounts/register.html', {
                'form_data': request.POST,
                'field_errors': field_errors,
                'errors': errors,
            })

        # Create user
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
        UserProfile.objects.get_or_create(user=user, defaults={'mobile': mobile})
        login(request, user)
        messages.success(request, f"Welcome to KenaKata, {first_name}! Your account has been created.")
        return redirect('dashboard:home')

    return render(request, 'accounts/register.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')

    client_ip = get_client_ip(request)
    next_url = request.POST.get('next', '') or request.GET.get('next', '')

    # Validate next_url to prevent Open Redirects (C3)
    if next_url:
        is_safe = url_has_allowed_host_and_scheme(
            url=next_url,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure()
        )
        if not is_safe:
            next_url = ''

    if request.method == 'POST':
        login_input = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')

        # Rate limiting / brute-force lockout (C5)
        rate_key = f"login_attempts_{client_ip}_{login_input.lower()}"
        ip_rate_key = f"login_attempts_ip_{client_ip}"
        attempts = max(cache.get(rate_key, 0), cache.get(ip_rate_key, 0))

        if attempts >= MAX_LOGIN_ATTEMPTS:
            messages.error(request, "Too many failed login attempts. Your account/IP is temporarily locked for 15 minutes.")
            return render(request, 'accounts/login.html', {
                'form_data': request.POST,
                'next': next_url,
                'has_error': True,
                'is_locked': True,
            })

        user = None
        # 1. Try directly with username
        user = authenticate(request, username=login_input, password=password)

        # 2. Try matching by email address (case-insensitive)
        if not user:
            matching_users = User.objects.filter(email__iexact=login_input)
            for m_user in matching_users:
                user = authenticate(request, username=m_user.username, password=password)
                if user:
                    break

        # 3. Try matching by mobile phone number
        if not user:
            clean_phone = re.sub(r'[\s\-\(\)]', '', login_input)
            if clean_phone:
                profile = UserProfile.objects.filter(mobile__icontains=clean_phone[-10:]).first()
                if profile and profile.user:
                    user = authenticate(request, username=profile.user.username, password=password)

        if user:
            # Reset rate limit on successful authentication
            cache.delete(rate_key)
            cache.delete(ip_rate_key)
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            return redirect(next_url or 'dashboard:home')
        else:
            new_attempts = attempts + 1
            cache.set(rate_key, new_attempts, timeout=LOCKOUT_SECONDS)
            cache.set(ip_rate_key, new_attempts, timeout=LOCKOUT_SECONDS)

            if new_attempts >= MAX_LOGIN_ATTEMPTS:
                messages.error(request, "Too many failed login attempts. Your account/IP is temporarily locked for 15 minutes.")
            else:
                messages.error(request, "Invalid email or password. Please check and try again.")

            return render(request, 'accounts/login.html', {
                'form_data': request.POST,
                'next': next_url,
                'has_error': True,
            })

    return render(request, 'accounts/login.html', {'next': next_url})


def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('/')
