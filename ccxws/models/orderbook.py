from pydantic import BaseModel


class quote(BaseModel):
    price: float
    amount: float

    def __lt__(self, other):
        return self.price < other.price

    def __le__(self, other):
        return self.price <= other.price

    def __gt__(self, other):
        return self.price > other.price

    def __ge__(self, other):
        return self.price >= other.price


class simple_orderbook(BaseModel):
    exchange: str
    symbol: str
    asks: list[quote]
    bids: list[quote]


class orderbook(BaseModel):
    exchange: str
    symbol: str
    asks: dict[str, quote]
    bids: dict[str, quote]

    def to_simple_orderbook(self):
        return simple_orderbook(
            exchange=self.exchange,
            symbol=self.symbol,
            asks=list(self.asks.values()),
            bids=list(self.bids.values())
        )

    def insert_ask(self, id: str, q: quote):
        self.asks[id] = q

    def insert_bid(self, id: str, q: quote):
        self.bids[id] = q

    def delete_order(self, id: str):
        if id in self.asks.keys():
            self.asks.pop(id)
        if id in self.bids.keys():
            self.bids.pop(id)

    def from_snapshot(self, asks: dict[id: str, quote], bids: dict[id: str, quote]):
        self.asks = asks
        self.bids = bids
