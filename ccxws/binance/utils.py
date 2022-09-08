from ..models import execution
from ..models import quote
from ..models import user_execution

import ast
import uuid


def to_execution(data):
    return execution(
        exchange='binance',
        symbol=data['s'],
        timestamp=data['T'],
        price=data['p'],
        amount=data['q'],
        taker_side='buy' if data['m'] else 'sell',
        sell_order_id=data['b'],
        buy_order_id=data['a']
    )


def to_orderbook_snapshot(data):
    asks = {}
    bids = {}
    for order in data['b']:
        bids[order[0]] = quote(
            price=order[0],
            amount=order[1])
    for order in data['a']:
        asks[order[0]] = quote(
            price=order[0],
            amount=order[1])
    return {'asks': asks, 'bids': bids}


def convert_symbol(symbol: str):
    if not symbol.isupper() and len(symbol.split('/')) != 2:
        raise Exception("invalid format. symbol must be like 'BTC/USDT'")
    first, second = symbol.split('/')
    return (first + second).lower()
