# run_telegram_bot.py
print("[command] Esecuzione comando run_telegram_bot")

from django.core.management.base import BaseCommand
from service_telegram.client import start_client, client
from service_telegram import handlers

class Command(BaseCommand):
    help = "Esegui il bot Telegram"

    def handle(self, *args, **kwargs):
        print("[command] Avvio client Telegram")
        start_client()

        print("[command] Registro gli handler")
        handlers.register_handlers()

        print("[command] Eseguo client.run_until_disconnected() (bloccante)")
        client.run_until_disconnected()
        print("[command] client.run_until_disconnected() terminato")
