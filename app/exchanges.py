import httpx

BINANCE_URL = "https://api.binance.com/api/v3/ticker/bookTicker"

async def get_binance_prices(symbol: str) -> dict:
    async with httpx.AsyncClient(timeout=3.0) as client:
        response = await client.get(BINANCE_URL, params={"symbol": symbol})
        response.raise_for_status()
        data = response.json()
        

    return {
        "exchange" : "binance",
        "symbol" : symbol,
        "bid" : float(data["bidPrice"]),
        "ask" : float(data["askPrice"])
    }


BYBIT_URL = "https://api.bybit.com/v5/market/tickers"

async def get_bybit_prices(symbol: str) -> dict:
    async with httpx.AsyncClient(timeout=3.0) as client:
        response = await client.get(BYBIT_URL, params={"symbol": symbol, "category": "spot"})
        response.raise_for_status()
        data = response.json()
        ticker = data["result"]["list"][0]
        
    
    return {
        "exchange": "bybit",
        "symbol": symbol,
        "bid": float(ticker["bid1Price"]),
        "ask": float(ticker["ask1Price"])
    }
