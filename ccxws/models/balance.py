from pydantic import BaseModel


class asset(BaseModel):
    symbol: str
    amount: float
    free: float
    frozen: float

class balance(BaseModel):
    exchange: str
    balance: list[asset]
    def from_ccxt(exchange, data):
        symbols = list(data.keys())
        symbols.remove('info')
        symbols.remove('free')
        symbols.remove('used')
        symbols.remove('total')
        if 'timestamp' in symbols:
            symbols.remove('timestamp')
        if 'datetime' in symbols:
            symbols.remove('datetime')
        return balance(
            exchange=exchange,
            balance=list(
                map(
                    lambda x: asset(
                        symbol=x,
                        amount=float(data[x]['free'])+float(data[x]['used']),
                        free=data[x]['free'],
                        frozen=data[x]['used']),
                    symbols
                )
            )
        )
