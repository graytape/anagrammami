from django.urls import path
from . import views

urlpatterns = [
    path('save-anagrams/', views.save_anagrams, name='save_anagrams'),
    path('delete-anagrams/', views.delete_anagrams, name='delete_anagrams'),
]