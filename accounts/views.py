from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import UserProfile
import re


def validate_bd_mobile(mobile):
    cleaned = re.sub(r'[\s\-\(\)]', '', mobile)
    pattern = r'^(\+880|880|0)?1[3-9]\d{8}$'
    return bool(re.match(pattern, cleaned))


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
        if not first_name:
            errors.append("First name is required.")
        if not email:
            errors.append("Email is required.")
        if not mobile:
            errors.append("Mobile number is required.")
        elif not validate_bd_mobile(mobile):
            errors.append("Please enter a valid Bangladesh mobile number (01XXXXXXXXX).")
        if not password:
            errors.append("Password is required.")
        elif len(password) < 8:
            errors.append("Password must be at least 8 characters.")
        if password != confirm_password:
            errors.append("Passwords do not match.")
        if User.objects.filter(email=email).exists():
            errors.append("An account with this email already exists.")
        if User.objects.filter(username=email).exists():
            errors.append("An account with this email already exists.")

        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'accounts/register.html', {'form_data': request.POST})

        # Create user
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
        UserProfile.objects.create(user=user, mobile=mobile)
        login(request, user)
        messages.success(request, f"Welcome to KenaKata, {first_name}! Your account has been created.")
        return redirect('dashboard:home')

    return render(request, 'accounts/register.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')

    if request.method == 'POST':
        login_input = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        next_url = request.POST.get('next', '') or request.GET.get('next', '')

        # Support login with either username OR email (e.g. Gmail)
        user = authenticate(request, username=login_input, password=password)
        if not user:
            # Check by email address
            matching_user = User.objects.filter(email__iexact=login_input).first()
            if matching_user:
                user = authenticate(request, username=matching_user.username, password=password)

        if user:
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            return redirect(next_url or 'dashboard:home')
        else:
            messages.error(request, "Invalid email/username or password.")
            return render(request, 'accounts/login.html', {'form_data': request.POST, 'next': next_url})

    next_url = request.GET.get('next', '')
    return render(request, 'accounts/login.html', {'next': next_url})


def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('/')
