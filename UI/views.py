from django.shortcuts import render,redirect
from django.urls import reverse
from django.contrib import messages

from django.contrib.auth.views import LoginView, logout_then_login
from .forms import *

# Create your views here.

def index(request):
    return render(request, 'UI/index.html')

class login(LoginView):
    template_name = "UI/login.html"
    redirect_authenticated_user = True

def register(request):
    if request.user.is_authenticated:
        messages.error(request,"Please do not create duplicate accounts.")
        return redirect('UI:index')
    
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created. You can now log in.")
            return redirect(reverse("UI:login"))
    else:
        form = SignUpForm()

    return render(request, "UI/register.html", {"form": form})

def logout(request):
    return logout_then_login(request,login_url= reverse('UI:login'))