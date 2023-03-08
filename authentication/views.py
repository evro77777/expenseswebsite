from django.core.mail import EmailMessage
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
import json
from django.http import JsonResponse
from django.contrib.auth.models import User
from validate_email import validate_email
from django.contrib import messages, auth

from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from .utils import token_generator

from django.contrib.auth.tokens import  default_token_generator
import threading
import environ

env = environ.Env()
environ.Env.read_env()


class EmailThread(threading.Thread):
    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send(fail_silently=False)


class RegistrationView(View):
    @staticmethod
    def get(request):
        return render(request, 'authentication/register.html')

    @staticmethod
    def post(request):
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        context = {
            'fieldValues': request.POST
        }

        if not User.objects.filter(username=username).exists():
            if not User.objects.filter(email=email).exists():
                if len(password) < 6:
                    messages.error(request, 'Password too short')
                    return render(request, 'authentication/register.html', context=context)
                user = User.objects.create_user(username=username, email=email)
                user.set_password(password)
                user.is_active = False
                user.save()
                uid64 = urlsafe_base64_encode(force_bytes(user.pk))
                domain = get_current_site(request).domain
                link = reverse('activate', kwargs={'uid64': uid64, 'token': token_generator.make_token(user)})
                email_subject = 'Activate your account'
                activate_url = f'http://{domain}{link}'
                email_body = f'Hello, {user.username}. Please use this link to verify your account\n {activate_url}'
                email = EmailMessage(
                    email_subject,
                    email_body,
                    env('EMAIL_HOST_USER'),
                    [user.email],
                )
                EmailThread(email).start()
                messages.success(request, 'Account created. Check email. Link sent to email')
                return render(request, 'authentication/register.html')
            else:
                messages.error(request, 'A user with this email already exists. ')
        else:
            messages.error(request, 'A user with this nickname already exists.')
        return render(request, 'authentication/register.html')


class EmailValidationView(View):
    @staticmethod
    def post(request):
        data = json.loads(request.body)
        email = data['email']

        if not validate_email(email):
            return JsonResponse({'email_error': 'email is invalid'}, status=400)
        if User.objects.filter(email=email).exists():
            return JsonResponse({'email_error': 'sorry, email in use, chose another one'}, status=409)

        return JsonResponse({'email_valid': True})


class UsernameValidationView(View):
    @staticmethod
    def post(request):
        data = json.loads(request.body)
        username = data['username']

        if not str(username).isalpha():
            return JsonResponse({'username_error': 'username should only contain alphabetic characters'}, status=400)
        if User.objects.filter(username=username).exists():
            return JsonResponse({'username_error': 'sorry, username in use, chose another one'}, status=409)

        return JsonResponse({'username_valid': True})


class VerificationView(View):
    @staticmethod
    def get(request, uid64, token):
        uid = force_str(urlsafe_base64_decode(uid64))
        user = User.objects.get(pk=uid)
        if user.is_active:
            reverse('login')
        user.is_active = True
        user.save()
        messages.success(request, 'Account activated successfully')
        return redirect('login')


class LoginView(View):
    def get(self, request):
        return render(request, 'authentication/login.html')

    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']

        if username and password:
            user = auth.authenticate(username=username, password=password)

            if user:
                if user.is_active:
                    auth.login(request, user)
                    messages.success(request, f'Welcome, {user.username} ')
                    return redirect('expenses')
                else:
                    messages.error(request, 'Account is not activate, please check your email')
                    return render(request, 'authentication/login.html')
            else:
                messages.error(request, 'Invalid credentials')
                return render(request, 'authentication/login.html')
        else:
            messages.error(request, 'Please, fill all fields')
            return render(request, 'authentication/login.html')


class LogoutView(View):
    def post(self, request):
        auth.logout(request)
        messages.success(request, 'You have been logged out')
        return redirect('login')


class RequestPasswordResetEmail(View):
    def get(self, request):
        return render(request, 'authentication/reset_password.html')

    def post(self, request):
        email = request.POST['email']
        if not validate_email(email):
            messages.error(request, 'Please supply a valid email')
            return render(request, 'authentication/reset_password.html')

        if not User.objects.filter(email=email).exists():
            messages.error(request, 'User not exists')
            return render(request, 'authentication/reset_password.html')

        user = User.objects.get(email=email)
        uid64 = urlsafe_base64_encode(force_bytes(email))
        domain = get_current_site(request).domain
        link = reverse('set_password', kwargs={'uid64': uid64, 'token': default_token_generator.make_token(user=user)})
        email_subject = 'Reset your password'
        reset_password_url = f'http://{domain}{link}'
        email_body = f'Hello, {email}. Link active 3 hours. Please use this link to reset your password\n ' \
                     f'{reset_password_url}.'
        email = EmailMessage(
            email_subject,
            email_body,
            env('EMAIL_HOST_USER'),
            [email],
        )
        EmailThread(email).start()
        messages.success(request, 'Check email. Link sent to email')

        return render(request, 'authentication/reset_password.html')


class VerificationResetPassword(View):
    @staticmethod
    def get(request, uid64, token):
        email = force_str(urlsafe_base64_decode(uid64))
        user = User.objects.get(email=email)
        if default_token_generator.check_token(user, token):
            context = {
                'uid64': uid64,
                'token': token
            }
            return render(request, 'authentication/set_password.html', context)
        else:
            return render(request, 'authentication/link_expired.html')

    @staticmethod
    def post(request, uid64, token):
        context = {
            'uid64': uid64,
            'token': token
        }
        email = force_str(urlsafe_base64_decode(uid64))
        user = User.objects.get(email=email)
        password = request.POST['password']
        repeat_password = request.POST['repeat_password']

        if len(password) < 6:
            messages.error(request, 'Password too short')
            return render(request, 'authentication/set_password.html', context)

        if password != repeat_password:
            messages.error(request, 'Password mismatch')
            return render(request, 'authentication/set_password.html', context)
        else:
            user.set_password(password)
            user.save()
            messages.success(request, 'Password changed')
            return redirect('login')
