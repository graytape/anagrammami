from django.shortcuts import render, redirect
from .forms import RegisterForm, LoginForm
from django.contrib.auth.models import User as AuthUser
from django.contrib.auth import login, authenticate, logout
from django.utils.translation import gettext as _


# Create your views here.
def register_view(request):
    if request.user.is_authenticated:
        return redirect('index')
    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            new_user = AuthUser(
                username=username,
            )
            new_user.set_password(password)
            new_user.save()
            login(request, new_user)

            return redirect('index')
        else:
            return render(request, 'register.html', {'form': form})
    else:
        form = RegisterForm()

    return render(request, 'register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('index')
    error_message = ''

    if request.method == 'POST':
        form = LoginForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('index')
            
            error_message = _('Wrong username or password')
            return render(request, 'login.html', {'form': form, 'error': error_message})
        else:
            return render(request, 'login.html', {'form': form, 'error': error_message})
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form, 'error': error_message})

def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        return redirect('index')
    return redirect('index')