# service_telegram/handlers.py
print("[handlers.py] Importazione handler")

from telethon import events
from .client import client
from service_anagrams.utils import generate_anagrams
import logging

logger = logging.getLogger(__name__)

MAX_MESSAGE_LENGTH = 4000  # 4096 è limite ufficiale, lascio un po' di margine

def chunk_anagrams(anagrams):
    """
    Riceve una lista di anagrammi (stringhe).
    Restituisce una lista di messaggi stringa, 
    ognuno <= MAX_MESSAGE_LENGTH caratteri.
    """
    chunks = []
    current_chunk = ""

    for anagram in anagrams:
        # +1 per il '\n' che aggiungiamo
        addition = anagram + "\n"

        # Se aggiungere questo anagramma supera il limite,
        # allora chiudo il chunk corrente e ne inizio uno nuovo.
        if len(current_chunk) + len(addition) > MAX_MESSAGE_LENGTH:
            chunks.append(current_chunk.rstrip())  # tolgo spazio finale/newline
            current_chunk = addition
        else:
            current_chunk += addition

    # Aggiungo l'ultimo chunk se non vuoto
    if current_chunk:
        chunks.append(current_chunk.rstrip())

    return chunks


def register_handlers():
    print("[handlers.py] Registrazione handler sul client")

    @client.on(events.NewMessage(incoming=True))
    async def on_new_message(event):

        if event.raw_text.strip() == '/start':
            await event.respond(f"Bot per la produzione di anagrammi, mandami una parola o un nome da anagrammare")
            return
        print(f"[handlers.py] Messaggio ricevuto da @{event.sender.username}: {event.raw_text}")

        word = event.raw_text.strip() if event.raw_text else ""
        if not word:
            print("[handlers.py] Messaggio vuoto, ignorato")
            return

        anagrams = generate_anagrams(word, None, None, 500)

        if not anagrams['success']:
            await event.respond("Nessun anagramma trovato.")
            return
        
        corpus_name = anagrams.get('corpus') or 'corpus predefinito'
        await event.respond(
            f"Trovati {anagrams['n_results']} anagrammi "
            f"(corpus: {corpus_name}) "
            f"con {anagrams['recursion']} ricorsioni e {anagrams['words']} parole completate:"
        )


        chunks = chunk_anagrams(anagrams['anagrams'])
        for chunk in chunks:
            await event.respond(chunk)

