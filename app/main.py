import asyncio
from fastapi import FastAPI, HTTPException, Depends
from app.exchanges import EXCHANGES
from app.database import engine, get_db, Base
from app.models import PriceSnapshot
from sqlalchemy.orm import Session



app = FastAPI(title="Crypto Spread Aggregator")

Base.metadata.create_all(bind=engine)

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

    buy_bybit_sell_binance = prices[0]["bid"] - prices[1]["ask"]
    buy_binance_sell_bybit = prices[1]["bid"] - prices[0]["ask"]

    return {
        "symbol": symbol,
        "prices": prices,
        "spreads": [
            {
                "direction": "buy_bybit_sell_binance",
                "raw": round(buy_bybit_sell_binance, 2),
                "raw_pct": round(buy_bybit_sell_binance / prices[1]["ask"] * 100, 4),
            },
            {
                "direction": "buy_binance_sell_bybit",
                "raw": round(buy_binance_sell_bybit, 2),
                "raw_pct": round(buy_binance_sell_bybit / prices[0]["ask"] * 100, 4),
            },
        ],
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