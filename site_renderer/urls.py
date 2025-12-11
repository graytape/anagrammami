from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("my-anagrams", views.my_anagrams, name="my-anagrams"),
]