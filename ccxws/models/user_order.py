import datetime

from pydantic import  BaseModel

class user_order(BaseModel):
    id: str
    price: float
    amount: float
    side: str
    filled: float
    symbol: str
    created_at: datetime.datetime
    updated_at: datetime.datetime

class simple_user_order_list(BaseModel):
    orders: list[user_order]

class user_order_list(BaseModel):
    order_list: dict[str, user_order]
    def to_simple_user_order_list(self):
        return simple_user_order_list(
            orders=list(self.order_list.values())
        )
