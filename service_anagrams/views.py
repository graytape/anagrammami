from django.shortcuts import render
from .utils import generate_anagrams
from django.http import JsonResponse


def fetch_hints(request, lang, chars):
    # 1. Ricevi la stringa
    chars = chars.strip()

    # 2. Calcolo dei suggerimenti (simulato)
    hints = generate_anagrams(chars, lang)   # tua funzione custom

    # 3. Render HTML del blocco da inserire
    #html = render_to_string("partials/hints_list.html", {
    #    "hints": hints
    #})

    # 4. Risposta JSON
    return JsonResponse({
        "status": "success",
        "hints_html": hints.get('anagrams', []),
        "n_results": hints.get('n_results', 0),
        "recursions": hints.get('recursion', 0)
    })