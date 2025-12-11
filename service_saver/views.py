import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import Anagrams

@login_required
@require_POST
def save_anagrams(request):
    try:
        data = json.loads(request.body)
        
        model = data.get('model')
        anagrams   = data.get('anagrams', '')

        if model and anagrams:
            Anagrams.objects.create(
                user=request.user,
                model=model,
                anagrams=anagrams
            )
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
@login_required
@require_POST
def delete_anagrams(request):
    data = json.loads(request.body)
    id = data.get('id')
    print(f"Deleting anagram entry with id: {id} for user: {request.user}")
    try:
        anagram_entry = Anagrams.objects.get(id=id, user=request.user)
        anagram_entry.delete()
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)