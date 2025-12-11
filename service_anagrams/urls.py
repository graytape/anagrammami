from django.urls import path

from . import views

urlpatterns = [
    path("<str:lang>/fetch/<str:chars>/", views.fetch_hints, name="fetch_hints"),
]