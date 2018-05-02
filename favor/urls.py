from django.urls import path, include
from . import views

urlpatterns = [
    path('favor_count', views.favor_count, name="favor_count"),
]