import logging

import httpx

from app.cache import redis_client
from app.config import settings

logger = logging.getLogger(__name__)


async def send_alert(text: str, symbol: str, direction: str) -> None:
    if not settings.telegram_bot_token or not settings.telegram_chat_id:
        logger.warning(
            "Telegram not configured "
            "(set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID); alert skipped"
        )
        return

    key = f"alert:{symbol}:{direction}"

    try:
        if redis_client.exists(key):
            return
    except Exception as e:
        logger.error("Redis dedup check failed, sending anyway: %s", e)

    url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            response = await client.post(
                url,
                json={"chat_id": settings.telegram_chat_id, "text": text},
            )
            response.raise_for_status()
    except Exception as e:
        logger.error("Failed to send Telegram alert: %s", e)
        return

    try:
        redis_client.setex(key, settings.alert_ttl, "1")
    except Exception as e:
        logger.error("Redis setex failed: %s", e)
