from pydantic import BaseModel
from datetime import datetime


class execution(BaseModel):
    exchange: str
    symbol: str
    timestamp: datetime
    price: float
    amount: float
    taker_side: str
    sell_order_id: str
    buy_order_id: str

