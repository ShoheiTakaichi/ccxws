from ..models import execution
from ..models import quote
from ..models import user_execution


def to_orderbook_snapshot(data):
    asks = {}
    bids = {}
    for order in data['asks']:
        asks[order['price']] = quote(
            price=order['price'],
            amount=order['size']
        )
    for order in data['bids']:
        bids[order['price']] = quote(
            price=order['price'],
            amount=order['size']
        )
    return {'asks': asks, 'bids': bids}

# before

def to_execution(symbol, data):
    return execution(
        exchange='bitfinex',
        symbol=symbol,
        timestamp=data['timestamp'],
        price=data['price'],
        amount=data['quantity'],
        taker_side=data['taker_side'],
        sell_order_id=data['sell_order_id'],
        buy_order_id=data['buy_order_id']
    )


def convert_symbol(symbol: str):
    if not symbol.isupper() and len(symbol.split('/')) != 2:
        raise Exception("invalid format. symbol must be like 'BTC/USDT'")
    first, second = symbol.split('/')
    return 'FX_'+first + '_' +second


def to_user_execution(symbol, data):
    return user_execution(
        symbol=symbol,
        taker_side=data['taker_side'],
        my_side=data['my_side'],
        price=data['price'],
        amount=data['quantity'],
        timestamp=data['timestamp'],
        order_id=data['order_id'],
        trade_id=''
    )


def to_user_order(data):
    return user_execution(
        id=str(data['id']),
        symbol=data['currency_pair_code'],
        amount=data['quantity'],
        filled=data['filled_quantity'],
        side=data['side'],
        price=data['price'],
        created_at=data['created_at'],
        updated_at=data['updated_at']
    )
