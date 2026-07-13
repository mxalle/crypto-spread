import asyncio

from fastapi import FastAPI

from app.exchanges import get_binance_prices, get_bybit_prices

app = FastAPI(title="Crypto Spread Aggregator")


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/spread")
async def spread(symbol: str = "BTCUSDT"):
    binance, bybit = await asyncio.gather(
        get_binance_prices(symbol),
        get_bybit_prices(symbol),
    )

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
