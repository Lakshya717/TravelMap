from django.shortcuts import render
from django.urls import reverse

from django.contrib.auth.views import LoginView, logout_then_login

# Create your views here.

def index(request):
    return render(request, 'UI/index.html')

class login(LoginView):
    template_name = "UI/login.html"
    redirect_authenticated_user = True

# def register(request):
#     return 

def logout(request):
    return logout_then_login(request,login_url= reverse('UI:login'))