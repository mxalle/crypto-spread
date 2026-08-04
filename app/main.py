import asyncio
from contextlib import asynccontextmanager
from itertools import combinations
from fastapi import FastAPI, HTTPException, Depends
from app.exchanges import EXCHANGES
from app.database import engine, get_db, Base
from app.models import PriceSnapshot
from app.scheduler import scheduler, start_scheduler
from sqlalchemy.orm import Session


Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    yield
    scheduler.shutdown()


app = FastAPI(title="Crypto Spread Aggregator", lifespan=lifespan)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/spread")
async def spread(symbol: str = "BTCUSDT", db: Session = Depends(get_db)):
    tasks = [exchange.get_prices(symbol) for exchange in EXCHANGES]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    prices = [result for result in results if isinstance(result, dict)]

    if not prices:
        raise HTTPException(status_code=502, detail="All exchange requests failed")

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

    spreads = []
    for a, b in combinations(prices, 2):
        buy_b_sell_a = a["bid"] - b["ask"]
        buy_a_sell_b = b["bid"] - a["ask"]
        spreads.append({
            "direction": f"buy_{b['exchange']}_sell_{a['exchange']}",
            "raw": round(buy_b_sell_a, 2),
            "raw_pct": round(buy_b_sell_a / b["ask"] * 100, 4),
        })
        spreads.append({
            "direction": f"buy_{a['exchange']}_sell_{b['exchange']}",
            "raw": round(buy_a_sell_b, 2),
            "raw_pct": round(buy_a_sell_b / a["ask"] * 100, 4),
        })

    return {
        "symbol": symbol,
        "prices": prices,
        "spreads": spreads,
    }


@app.get("/history")
def history(
    symbol: str = "BTCUSDT",
    exchange: str | None = None,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    query = db.query(PriceSnapshot)

    query = query.filter(
        PriceSnapshot.symbol == symbol
    )

    if exchange:
        query = query.filter(
            PriceSnapshot.exchange == exchange
        )

    query = query.order_by(
        PriceSnapshot.timestamp.desc()
    )

    query = query.limit(limit)

    snapshots = query.all()

    return [
        {
            "exchange": snapshot.exchange,
            "symbol": snapshot.symbol,
            "bid": snapshot.bid,
            "ask": snapshot.ask,
            "timestamp": snapshot.timestamp,
        }
        for snapshot in snapshots
    ] 