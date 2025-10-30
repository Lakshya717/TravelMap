from django.urls import path
from . import views

app_name = 'UI'
urlpatterns = [
	path("",views.index,name="index"),
	path("login/",views.login.as_view(),name="login"),
	path("logout/",views.logout,name="logout"),
]