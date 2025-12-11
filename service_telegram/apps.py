import os
import threading
import logging
import asyncio
from django.apps import AppConfig
from django.conf import settings
from .client import client, start_client_async
from . import handlers

logger = logging.getLogger(__name__)

class ServiceTelegramConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "service_telegram"

    def ready(self):
        """
        Avvia il bot Telegram in un thread separato all'avvio del server Django.
        """

        # Debug autoreload: evitare doppio avvio in modalità DEBUG di runserver
        if settings.DEBUG and os.environ.get("RUN_MAIN") != "true":
            logger.info("Autoreload: salto avvio bot per evitare doppio thread.")
            return

        logger.info("Avvio thread bot Telegram da AppConfig.ready()...")

        def start_bot():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self.async_start_bot())
            except Exception as e:
                logger.exception(f"[apps.py] Errore nel bot thread: {e}")

        threading.Thread(
            target=start_bot, 
            name="telegram-bot-thread",
            daemon=True
        ).start()

    async def async_start_bot(self):
        await start_client_async()
        handlers.register_handlers()
        logger.info("[apps.py] Bot avviato, run_until_disconnected…")
        await client.run_until_disconnected()