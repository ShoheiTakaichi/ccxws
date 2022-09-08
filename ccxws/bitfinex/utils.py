from ..models import execution
from ..models import quote
from ..models import user_execution


def to_execution(symbol, data):
    return execution(
        exchange='bitfinex',
        symbol=symbol,
        timestamp=data[1],
        price=data[3],
        amount=abs(data[2]),
        taker_side='sell' if data[2] < 0 else 'buy',
        sell_order_id='',
        buy_order_id=''
    )


def to_orderbook_snapshot(data):
    asks = {}
    bids = {}
    for order in data:
        if order[2] > 0:
            bids[order[0]] = quote(price=order[1], amount=order[2])
        if order[2] < 0:
            asks[order[0]] = quote(price=order[1], amount=-order[2])
    return {'asks': asks, 'bids': bids}


def convert_symbol(symbol: str):
    if not symbol.isupper() and len(symbol.split('/')) != 2:
        raise Exception("invalid format. symbol must be like 'BTC/USD'")
    first, second = symbol.split('/')
    if second == 'USDT':
        second = 'UST'
    if len(first) > 3:
        first = first + ':'
    print(first + second)
    return first + second


def to_user_execution(symbol, data):
    return user_execution(
        symbol=symbol,
        timestamp=data[2],
        taker_side='buy' if -data[8] * data[4] > 0 else 'sell',
        price=data[5],
        amount=abs(data[4]),
        my_side='buy' if data[4] > 0 else 'sell',
        order_id=data[3],
        trade_id=''
    )


def to_user_order(data):
    return user_execution(
        id=str(data[2][0]),
        currency_pair_code=data[2][3][1:],
        amount=abs(data[2][7]),
        filled=abs(data[2][7]) - abs(data[2][6]),
        side='sell' if data[2][6] < 0 else 'buy',
        price=data[2][16],
        created_at=data[2][4],
        updated_at=data[2][5]
    )
