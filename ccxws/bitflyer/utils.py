import datetime
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

"""
{'buy_child_order_acceptance_id': 'JRF20221024-094318-146678',
                         'exec_date': '2022-10-24T09:43:18.7868824Z',
                         'id': 2401318453,
                         'price': 2896010.0,
                         'sell_child_order_acceptance_id': 'JRF20221024-094318-153326',
                         'side': 'SELL',
                         'size': 0.02}
"""

def to_execution(symbol, data):
    return execution(
        exchange='bitflyer',
        symbol=symbol,
        timestamp=datetime.datetime.strptime(data['exec_date'][0:-2], '%Y-%m-%dT%H:%M:%S.%f'),
        price=data['price'],
        amount=data['size'],
        taker_side=data['side'],
        sell_order_id='',
        buy_order_id=''
    )


def convert_symbol(symbol: str):
    if not symbol.isupper() and len(symbol.split('/')) != 2:
        raise Exception("invalid format. symbol must be like 'BTC/USDT'")
    first, second = symbol.split('/')
    return 'FX_'+first + '_' +second

# before

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
