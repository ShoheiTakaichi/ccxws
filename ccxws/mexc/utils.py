from ..models import execution
from ..models import quote
from ..models import user_execution
from ..models import user_order


def to_execution(symbol, data):
    return execution(
        exchange='mexc',
        symbol=symbol,
        timestamp=data['t'],
        taker_side='buy' if data['T'] == 2 else 'sell',
        price=float(data['p']),
        amount=float(data['q']),
        sell_order_id='',
        buy_order_id=''
    )


def to_orderbook_snapshot(data):
    asks = {}
    bids = {}
    for q in data['asks']:
        asks[q[0]] = quote(price=float(q[0]), amount=float(q[1]))
    for q in data['bids']:
        bids[q[0]] = quote(price=float(q[0]), amount=float(q[1]))
    return {'asks': asks, 'bids': bids}


def convert_symbol(symbol: str, reverse: bool = False):
    if reverse:
        return symbol.replace('_', '/')
    return symbol.replace('/', '_')


def to_user_execution(symbol, data):
    try:
        return user_execution(
            symbol=symbol,
            timestamp=data['t'],
            taker_side='sell' if (data['isTaker'] == 1 and data['T'] == 2) or (
                    data['isTaker'] != 1 and data['T'] != 2) else 'buy',
            price=float(data['p']),
            amount=float(data['q']),
            my_side='buy' if data['T'] == 1 else 'sell',
            order_id=data['id'],
            trade_id=data['tradeId']
        )
    except:
        print('error in ccxws mexc util 38')


def to_user_order(symbol, data):
    return user_order(
        id=data['id'],
        symbol=symbol,
        amount=data['quantity'],
        filled=data['remainQuantity'],
        side='sell' if data['tradeType'] == 2 else 'buy',
        price=data['price'],
        created_at=data['createTime'],
        updated_at=data['createTime']
    )
