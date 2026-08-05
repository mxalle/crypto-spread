# Screenshots

The project README expects two images in this folder. Add them with these exact
filenames so the links in `../README.md` resolve:

## 1. `swagger.png` — the OpenAPI docs

1. Run the app: `uvicorn app.main:app --reload`
2. Open `http://127.0.0.1:8000/docs`
3. Expand `/spread` (and optionally `/history`) so the response **schema** is visible.
4. Screenshot the page and save it here as `swagger.png`.

## 2. `telegram.png` — a real alert in Telegram

Live BTCUSDT spreads are tiny (~0.005 %), below the default `SPREAD_THRESHOLD=0.05`,
so an alert won't fire on its own. To capture one:

1. In `.env`, temporarily set `SPREAD_THRESHOLD=0.001`.
2. Make sure `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` are filled in.
3. Restart the app and wait one scheduler cycle (~30 s) for a message to arrive.
4. Screenshot the alert in your Telegram chat and save it here as `telegram.png`.
5. Restore `SPREAD_THRESHOLD=0.05` in `.env`.
