from django.shortcuts import render
from django.contrib.auth.models import User
from service_saver.models import Anagrams
import markdown

# Create your views here.
def index(request):
    return render (request, 'main.html', {})

def my_anagrams(request):
    if not request.user.is_authenticated:
        return render(request, 'my-anagrams.html', {'anagrams': []})

    all_anagrams = Anagrams.objects.filter(
        user_id=request.user.id
    ).values('id', 'model', 'anagrams', 'create_date').order_by('-create_date')

    md = markdown.Markdown(extensions=['nl2br'])

    anagrams_cleaened = []
    for anagram in all_anagrams:
        anagram['anagrams'] = anagram['anagrams'] or ""
        anagrams_cleaened.append(anagram)
        print(anagram)
    return render(request, 'my-anagrams.html', {'anagrams': anagrams_cleaened})