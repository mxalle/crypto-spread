from fastapi import FastAPI

app = FastAPI(title="Crypto Spread  Aggregator")

@app.get("/health")
async def health():
    return {"status":"ok"}

