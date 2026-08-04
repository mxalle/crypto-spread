import asyncio

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.database import SessionLocal
from app.exchanges import EXCHANGES
from app.models import PriceSnapshot

SYMBOL = "BTCUSDT"

scheduler = AsyncIOScheduler()


async def collect_prices() -> None:
    tasks = [exchange.get_prices(SYMBOL) for exchange in EXCHANGES]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    prices = [result for result in results if isinstance(result, dict)]
    if not prices:
        return

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
    scheduler.add_job(collect_prices, "interval", seconds=30)
    scheduler.start()
