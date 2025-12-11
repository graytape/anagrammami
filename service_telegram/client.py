import logging
from telethon import TelegramClient
from django.conf import settings

logger = logging.getLogger(__name__)

# Crea il client Telethon
client = TelegramClient(
    "bot_session",
    settings.TELEGRAM_API_ID,
    settings.TELEGRAM_API_HASH
)

# Funzione ASINCRONA necessaria nel thread separato
async def start_client_async():
    logger.info("[client.py] Avvio async del bot Telegram…")
    await client.start(bot_token=settings.TELEGRAM_BOT_TOKEN)
    logger.info("[client.py] Client Telegram avviato correttamente (async).")