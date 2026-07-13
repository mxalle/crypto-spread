import asyncio

from app.exchanges import get_binance_prices, get_bybit_prices


async def main():
    binance = await get_binance_prices("BTCUSDT")
    print(binance)

    bybit = await get_bybit_prices("BTCUSDT")
    print(bybit)

asyncio.run(main())