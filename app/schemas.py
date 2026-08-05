from datetime import datetime

from pydantic import BaseModel, ConfigDict


class HealthOut(BaseModel):
    status: str


class PriceOut(BaseModel):
    exchange: str
    symbol: str
    bid: float
    ask: float


class SpreadOut(BaseModel):
    direction: str
    raw: float
    raw_pct: float


class SpreadResponse(BaseModel):
    symbol: str
    prices: list[PriceOut]
    spreads: list[SpreadOut]


class PriceSnapshotOut(PriceOut):
    model_config = ConfigDict(from_attributes=True)

    timestamp: datetime
