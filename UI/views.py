from django.shortcuts import render,redirect
from django.urls import reverse
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
import json
import requests


from django.contrib.auth.views import LoginView, logout_then_login
from django.contrib.auth.decorators import login_required

from .forms import *
from Accounts.models import *
from django.views.decorators.http import require_http_methods

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
def edit_travelplan(request, pk: int):
    """Edit an existing TravelPlan and its nested Trips using the same forms/formset as creation.

    - Reuses TravelPlanForm and TripFormSet
    - Supports adding new trips and deleting existing ones (via formset can_delete)
    """
    try:
        plan = (
            TravelPlan.objects
            .select_related('user')
            .prefetch_related('trips')
            .get(pk=pk)
        )
    except TravelPlan.DoesNotExist:
        messages.error(request, "Travel plan not found.")
        return redirect('UI:travelplans')

    # Optional: permission check (owner-only edits)
    if plan.user_id != request.user.id:
        messages.error(request, "You don't have permission to edit this plan.")
        return redirect('UI:travelplan_detail', pk=plan.pk)

    if request.method == 'POST':
        plan_form = TravelPlanForm(request.POST, instance=plan)
        formset = TripFormSet(request.POST, instance=plan)
        if plan_form.is_valid() and formset.is_valid():
            plan_form.save()
            formset.save()
            messages.success(request, "Travel plan updated.")
            return redirect('UI:travelplan_detail', pk=plan.pk)
    else:
        plan_form = TravelPlanForm(instance=plan)
        formset = TripFormSet(instance=plan)

    # Reuse the same template as creation
    return render(request, 'UI/travelplans_new.html', {
        'plan_form': plan_form,
        'formset': formset,
        'plan': plan,
        'is_edit': True,
    })

@login_required
def travelplan_detail(request, pk: int):
    plan = (
        TravelPlan.objects
        .select_related('user')
        .prefetch_related('trips__passengers', 'chat_messages__user')
        .get(pk=pk)
    )
    messages_qs = plan.chat_messages.all().select_related('user')
    return render(request, 'UI/travelplan_detail.html', {
        'plan': plan,
        'trips': plan.trips.all(),
        'chat_messages': messages_qs,
    })

@login_required
@require_http_methods(["POST"])
def delete_travelplan(request, pk: int):
    """Delete a TravelPlan (owner or staff only).

    This endpoint expects a POST request and will redirect back to the
    user's travel plan list with a status message.
    """
    try:
        plan = (
            TravelPlan.objects
            .select_related('user')
            .get(pk=pk)
        )
    except TravelPlan.DoesNotExist:
        messages.error(request, "Travel plan not found.")
        return redirect('UI:travelplans')

    if not (request.user.is_staff or plan.user_id == request.user.id):
        messages.error(request, "You don't have permission to delete this plan.")
        return redirect('UI:travelplan_detail', pk=plan.pk)

    title = plan.title
    plan.delete()
    messages.success(request, f"Deleted travel plan: {title}")
    return redirect('UI:my_travelplans')

@login_required
@require_POST
def cache_trip_route(request, pk: int):
    """Persist a computed route for a trip to avoid re-querying the routing engine.

    Expected JSON body: {
      "engine": "osrmv1",
      "coordinates": [[lat, lon], ...],
      "summary": {"totalDistance": Number, "totalTime": Number}
    }
    Only the plan owner (or staff) is allowed to cache routes for their trips.
    """
    try:
        trip = Trip.objects.select_related('plan', 'plan__user').get(pk=pk)
    except Trip.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'Trip not found'}, status=404)

    if not (request.user.is_staff or (trip.plan_id and trip.plan.user_id == request.user.id)):
        return JsonResponse({'ok': False, 'error': 'Forbidden'}, status=403)

    try:
        payload = json.loads(request.body.decode('utf-8') or '{}')
    except json.JSONDecodeError:
        return JsonResponse({'ok': False, 'error': 'Invalid JSON'}, status=400)

    coords = payload.get('coordinates')
    if not isinstance(coords, list) or not coords:
        return JsonResponse({'ok': False, 'error': 'Missing coordinates'}, status=400)

    # Basic normalization: ensure [lat, lon] pairs of floats
    norm = []
    for pair in coords:
        try:
            lat, lon = float(pair[0]), float(pair[1])
            norm.append([lat, lon])
        except Exception:
            continue
    if not norm:
        return JsonResponse({'ok': False, 'error': 'No valid coordinates'}, status=400)

    trip.route = {
        'engine': payload.get('engine') or 'osrmv1',
        'coordinates': norm,
        'summary': payload.get('summary') or {},
        'saved_at': timezone.now().isoformat()
    }
    trip.save(update_fields=['route', 'updated_at'])
    return JsonResponse({'ok': True})

@login_required
@require_http_methods(["GET", "POST"])
def chat_messages_api(request, pk: int):
    """Get or post chat messages for a TravelPlan.

    - GET: returns JSON list of messages [{id, user, content, created_at}]
    - POST: expects form-encoded or JSON {content}; creates message for current user
    """
    try:
        plan = TravelPlan.objects.get(pk=pk)
    except TravelPlan.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'Plan not found'}, status=404)

    if request.method == 'GET':
        msgs = (
            plan.chat_messages
            .select_related('user')
            .order_by('created_at')
        )
        data = [
            {
                'id': m.id,
                'user': m.user.username,
                'user_id': m.user_id,
                'content': m.content,
                'created_at': m.created_at.isoformat(),
            }
            for m in msgs
        ]
        return JsonResponse({'ok': True, 'messages': data})

    # POST
    content = None
    if request.content_type and 'application/json' in request.content_type:
        try:
            body = json.loads(request.body.decode('utf-8') or '{}')
            content = body.get('content')
        except json.JSONDecodeError:
            return JsonResponse({'ok': False, 'error': 'Invalid JSON'}, status=400)
    else:
        content = request.POST.get('content')

    if not content or not content.strip():
        return JsonResponse({'ok': False, 'error': 'Message content required'}, status=400)

    msg = ChatMessage.objects.create(
        plan=plan,
        user=request.user,
        content=content.strip()[:2000]
    )
    return JsonResponse({
        'ok': True,
        'message': {
            'id': msg.id,
            'user': request.user.username,
            'user_id': request.user.id,
            'content': msg.content,
            'created_at': msg.created_at.isoformat(),
        }
    }, status=201)


def map(request):
    """Render the live social map with all trips.

    Provides a JSON-serializable list of trips in context for the template
    to render with Leaflet and Leaflet Routing Machine (LRM).
    """
    trips = (
        Trip.objects
        .select_related('plan', 'plan__user')
        .all()
    )

    trip_list = []
    for t in trips:
        detail_url = None
        if t.plan_id:
            try:
                detail_url = reverse('UI:travelplan_detail', kwargs={'pk': t.plan_id})
            except Exception:
                detail_url = None

        trip_list.append({
            'id': t.id,
            'title': t.title,
            'plan_title': t.plan.title if t.plan_id else '',
            'plan_id': t.plan_id,
            'detail_url': detail_url,
            'owner': t.plan.user.username if t.plan_id else '',
            'origin_name': t.origin_name,
            'origin_lat': t.origin_lat or '',
            'origin_lon': t.origin_lon or '',
            'destination_name': t.destination_name,
            'destination_lat': t.destination_lat or '',
            'destination_lon': t.destination_lon or '',
            'departure_time': t.departure_time.isoformat() if t.departure_time else None,
            'estimated_arrival_time': t.estimated_arrival_time.isoformat() if t.estimated_arrival_time else None,
            'transport_mode': t.transport_mode,
            'route': t.route if hasattr(t, 'route') else None,
            'status': t.status,
        })

    return render(request, 'UI/map.html', {
        'trips': trip_list,
    })

def search_map(request):
    city = {
        'name': "IIT Kottayam",
        'center':[9.7553584,76.6482941],
        'cityBounds':[75.72052001953126,22.851931284116755,76.01852416992189,22.57750708339807]
    }

    # messages.success(request,'To manually select a location, press Search and then click on Manual Selection')
    return render(request,"search_map.html",{
        "city": city
    })

def geocode(request):
    if request.method == "GET":

        query = request.GET.get('query','')

        # Refer format at https://nominatim.org/release-docs/latest/api/Search/

        API_headers = {
            "User-Agent": "CityHub.me/Pre-Release-1.2 (https://cityhub-gyg8d5gcdygdgyg4.centralindia-01.azurewebsites.net/; lakshya_717@outlook.com)"
        }
        API_BASE = "https://nominatim.openstreetmap.org/search"
        API_PARAMS = {
            "format":"json",
            "addressdetails":1,
            "q": query,
            "limit": 10,
        }

        try:
            response = requests.get(API_BASE,params=API_PARAMS,headers=API_headers)
            response.raise_for_status()
            return JsonResponse(response.json(), safe=False)
        
        except requests.exceptions.RequestException as e:
            return JsonResponse({'error': str(e)}, status=500)

    else:
        return None
  
