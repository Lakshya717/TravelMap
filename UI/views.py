from django.shortcuts import render,redirect
from django.urls import reverse
from django.contrib import messages
from django.core.paginator import Paginator


from django.contrib.auth.views import LoginView, logout_then_login
from django.contrib.auth.decorators import login_required

from .forms import *
from Accounts.models import *

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


def travelplans(request):
    """List travel plans created by all users.

    Reuses templates/UI/travelplans.html and paginates results.
    """
    plans_qs = (
        TravelPlan.objects
        .select_related('user')
        .prefetch_related('trips__passengers')
    )

    paginator = Paginator(plans_qs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'UI/travelplans.html', {
        'page_obj': page_obj,
        'plans': page_obj.object_list,
    })

@login_required
def my_travelplans(request):
    plans_qs = (
        TravelPlan.objects
        .filter(user=request.user)
        .prefetch_related('trips__passengers')
    )

    paginator = Paginator(plans_qs, 10)  # 10 plans per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'UI/travelplans.html', {
        'page_obj': page_obj,
        'plans': page_obj.object_list,
        'personal':True
    })

@login_required
def new_travelplan(request):
    if request.method == 'POST':
        plan_form = TravelPlanForm(request.POST)
        if plan_form.is_valid():
            plan = plan_form.save(commit=False)
            formset = TripFormSet(request.POST, instance=plan)
            if formset.is_valid():
                plan.user = request.user
                plan.save()
                formset.instance = plan
                formset.save()
                return redirect('UI:travelplans')
        else:
            formset = TripFormSet(request.POST)
    else:
        plan_form = TravelPlanForm()
        formset = TripFormSet()

    return render(request, 'UI/travelplans_new.html', {
        'plan_form': plan_form,
        'formset': formset,
    })

@login_required
def map(request):
    return render(request,'UI/map.html')
