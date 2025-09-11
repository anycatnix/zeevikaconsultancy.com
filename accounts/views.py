from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib import messages

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful. You are now logged in.')
            return redirect('jobs:home')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = UserCreationForm()
    
    return render(request, 'registration/signup.html', {'form': form})
