import asyncio
from fastapi import FastAPI, HTTPException, Depends
import httpx
from app.exchanges import get_binance_prices, get_bybit_prices
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
    try: 
        binance, bybit = await asyncio.gather(
            get_binance_prices(symbol),
            get_bybit_prices(symbol),
    )
    except httpx.TimeoutException:
        raise HTTPException(status_code = 502, detail = "Exchange request timed out")
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=502,
            detail=f"Exchange returned error: {e.response.status_code}",
        )

    db.add_all([
        PriceSnapshot(
            exchange=binance["exchange"],
            symbol=binance["symbol"],
            bid=binance["bid"],
            ask=binance["ask"],
        ),
        PriceSnapshot(
            exchange=bybit["exchange"],
            symbol=bybit["symbol"],
            bid=bybit["bid"],
            ask=bybit["ask"],
        ),
    ])
    db.commit()
    
    buy_bybit_sell_binance = binance["bid"] - bybit["ask"]
    buy_binance_sell_bybit = bybit["bid"] - binance["ask"]

    return {
        "symbol": symbol,
        "prices": [binance, bybit],
        "spreads": [
            {
                "direction": "buy_bybit_sell_binance",
                "raw": round(buy_bybit_sell_binance, 2),
                "raw_pct": round(buy_bybit_sell_binance / bybit["ask"] * 100, 4),
            },
            {
                "direction": "buy_binance_sell_bybit",
                "raw": round(buy_binance_sell_bybit, 2),
                "raw_pct": round(buy_binance_sell_bybit / binance["ask"] * 100, 4),
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