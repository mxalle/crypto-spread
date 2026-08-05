import asyncio
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.config import settings
from app.database import SessionLocal
from app.exchanges import EXCHANGES
from app.models import PriceSnapshot
from app.notifier import send_alert
from app.spreads import calculate_spreads

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


async def collect_prices() -> None:
    tasks = [exchange.get_prices(settings.symbol) for exchange in EXCHANGES]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    prices = [result for result in results if isinstance(result, dict)]
    if not prices:
        return

    spreads = calculate_spreads(prices)
    for spread in spreads:
        if spread["raw_pct"] > settings.spread_threshold:
            logger.warning(
                "Spread alert: %s at %s%%",
                spread["direction"],
                spread["raw_pct"],
            )
            await send_alert(
                f"Spread alert on {settings.symbol}: {spread['direction']} "
                f"= {spread['raw_pct']}% (raw {spread['raw']})",
                settings.symbol,
                spread["direction"],
            )

    db = SessionLocal()
    try:
        db.add_all([
            PriceSnapshot(
                exchange=price["exchange"],
                symbol=price["symbol"],
                bid=price["bid"],
                ask=price["ask"],
            )
            for price in prices
        ])
        db.commit()
    finally:
        db.close()


def start_scheduler() -> None:
    scheduler.add_job(collect_prices, "interval", seconds=settings.collect_interval)
    scheduler.start()
