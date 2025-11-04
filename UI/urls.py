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
	path("travelplans/<int:pk>/edit/", views.edit_travelplan, name="edit_travelplan"),
	path("travelplans/<int:pk>/delete/", views.delete_travelplan, name="delete_travelplan"),
	path("travelplans/<int:pk>/", views.travelplan_detail, name="travelplan_detail"),
	path("api/travelplans/<int:pk>/chat/", views.chat_messages_api, name="chat_messages_api"),

	path("map/",views.map,name="map"),
	path("api/trips/<int:pk>/route", views.cache_trip_route, name="cache_trip_route"),
	path("search_map/",views.search_map,name="search_map"),
	path("geocode/", views.geocode, name="geocode"),
]