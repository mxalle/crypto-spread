import json

import httpx

from app.cache import redis_client

BINANCE_URL = "https://api.binance.com/api/v3/ticker/bookTicker"


async def get_binance_prices(symbol: str) -> dict:
    key = f"binance:{symbol}"

    cached = redis_client.get(key)
    if cached:
        return json.loads(cached)

    async with httpx.AsyncClient(timeout=3.0) as client:
        response = await client.get(BINANCE_URL, params={"symbol": symbol})
        response.raise_for_status()
        data = response.json()

    result = {
        "exchange": "binance",
        "symbol": symbol,
        "bid": float(data["bidPrice"]),
        "ask": float(data["askPrice"]),
    }

    await redis_client.setex(
        key,
        2,
        json.dumps(result)
    )

    return result


BYBIT_URL = "https://api.bybit.com/v5/market/tickers"


async def get_bybit_prices(symbol: str) -> dict:
    key = f"bybit:{symbol}"

    cached = redis_client.get(key)
    if cached:
        return json.loads(cached)

    async with httpx.AsyncClient(timeout=3.0) as client:
        response = await client.get(
            BYBIT_URL,
            params={"symbol": symbol, "category": "spot"},
        )
        response.raise_for_status()
        data = response.json()
        ticker = data["result"]["list"][0]

    result = {
        "exchange": "bybit",
        "symbol": symbol,
        "bid": float(ticker["bid1Price"]),
        "ask": float(ticker["ask1Price"]),
    }

    await redis_client.setex(
        key,
        2,
        json.dumps(result)
    )

    return result