import json
from abc import ABC, abstractmethod

import httpx

from app.cache import redis_client


class ExchangeClient(ABC):
    name: str

    @abstractmethod
    async def get_prices(self, symbol: str) -> dict:
        ...


class BinanceClient(ExchangeClient):
    name = "binance"
    URL = "https://api.binance.com/api/v3/ticker/bookTicker"

    async def get_prices(self, symbol: str) -> dict:
        key = f"prices:{self.name}:{symbol}"

        cached = redis_client.get(key)
        if cached:
            return json.loads(cached)

        async with httpx.AsyncClient(timeout=3.0) as client:
            response = await client.get(self.URL, params={"symbol": symbol})
            response.raise_for_status()
            data = response.json()

        result = {
            "exchange": "binance",
            "symbol": symbol,
            "bid": float(data["bidPrice"]),
            "ask": float(data["askPrice"]),
        }

        redis_client.setex(
            key,
            2,
            json.dumps(result)
        )

        return result


class BybitClient(ExchangeClient):
    name = "bybit"
    URL = "https://api.bybit.com/v5/market/tickers"

    async def get_prices(self, symbol: str) -> dict:
        key = f"prices:{self.name}:{symbol}"

        cached = redis_client.get(key)
        if cached:
            return json.loads(cached)

        async with httpx.AsyncClient(timeout=3.0) as client:
            response = await client.get(
                self.URL,
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

        redis_client.setex(
            key,
            2,
            json.dumps(result)
        )

        return result
