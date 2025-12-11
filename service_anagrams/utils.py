import os
from django.shortcuts import render
from .anagramgen_fork import AnagramGenerator

APP_DIR = os.path.dirname(os.path.abspath(__file__))

def generate_anagrams(word, lang=None, corpus=None, max=None):

    if lang is None or lang.lower() == 'it':
        lang = "it"
        folder = "italian"
        if corpus is None:
            corpus = "parole_uniche.txt"

        corpora = [
            'parole_uniche.txt',
            '1000_parole_italiane_comuni.txt',
            '60000_parole_italiane.txt',
            '280000_parole_italiane.txt',
            '660000_parole_italiane.txt'
        ]
        corpus = corpora[3]

    elif lang.lower() == 'en':
        lang = lang.lower()
        folder = 'english'
        if corpus is None:
            corpus = "top-5k.txt"

    


    corpus_path = os.path.join(APP_DIR, "data", folder, corpus)
    with open(corpus_path, 'r') as file:
        corpus_list = [line.strip() for line in file if line.strip() and line.strip().isalpha()]
    results = AnagramGenerator(corpus_list).generate(word)

    results['anagrams'] = [" ".join(anagram) for anagram in results.get('anagrams', [])]
    if max is not None:
        results['anagrams'] = results['anagrams'][:max]
    return results


