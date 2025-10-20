from django.urls import path
from . import views

app_name = 'UI'
urlpatterns = [
	path("",views.index,name="index")
]