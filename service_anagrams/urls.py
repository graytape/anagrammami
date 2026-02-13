from django.urls import path

from . import views

urlpatterns = [
    # Hints (anagram generation for unused characters)
    path("<str:lang>/fetch/<str:chars>/", views.fetch_hints, name="fetch_hints"),

    # Per-user settings (used by the web UI)
    path("settings/", views.get_user_settings, name="anagram_get_settings"),
    path("settings/save/", views.save_user_settings, name="anagram_save_settings"),
]