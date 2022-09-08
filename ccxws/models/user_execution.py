import datetime

from pydantic import BaseModel


class user_execution(BaseModel):
    symbol: str
    timestamp: datetime.datetime
    price: float
    amount: float
    taker_side: str
    order_id: str
    trade_id: str
    my_side: str
