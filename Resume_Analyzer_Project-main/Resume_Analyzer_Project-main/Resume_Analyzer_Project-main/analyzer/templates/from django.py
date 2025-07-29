from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.models import User
from django.db import IntegrityError
from .forms import RegisterForm
from .models import Profile

def signup_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password1']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']

            # Generate a unique username from email
            username = email.split('@')[0]
            original_username = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{original_username}{counter}"
                counter += 1

            try:
                # Create user with unique username
                user = User.objects.create_user(username=username, email=email, password=password,
                                                first_name=first_name, last_name=last_name)
                
                # Create associated Profile
                Profile.objects.create(
                    user=user,
                    phone=form.cleaned_data.get('phone', ''),
                    location=form.cleaned_data.get('location', ''),
                    title=form.cleaned_data.get('title', ''),
                    education=form.cleaned_data.get('education', '')
                )

                # Log the user in
                login(request, user)
                messages.success(request, f'Welcome, {user.first_name}! Your account has been created successfully.')
                return redirect('dashboard')
            except IntegrityError as e:
                messages.error(request, f"An error occurred: {str(e)}")
                return render(request, 'signup.html', {'form': form})
    else:
        form = RegisterForm()
    return render(request, 'signup.html', {'form': form})
