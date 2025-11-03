from django.urls import path
from . import views

app_name = 'UI'
urlpatterns = [
	path("",views.index,name="index"),
	path("login/",views.login.as_view(),name="login"),
	path("logout/",views.logout,name="logout"),
	path("register/",views.register,name="register"),

	path("travelplans/",views.travelplans,name="travelplans"),
	path("travelplans/me/",views.my_travelplans,name="my_travelplans"),
	path("travelplans/me/new/",views.new_travelplan,name="new_travelplan"),
	# path("new/trip/",views.new_trip,name="new_trip "),
	path("map/",views.map,name="map"),
	path("search_map/",views.search_map,name="search_map"),
	path("geocode/", views.geocode, name="geocode"),
]