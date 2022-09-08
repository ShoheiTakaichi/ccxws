import json
import time
from queue import Queue
from threading import Thread
import jwt
import websocket

from ccxws.iwebsocket import iwebsocket
from ccxws.ccxt_delegator import CcxtDelegator
from ccxws.utils import orderbook, user_order, user_execution, execution

from ..models import orderbook, quote, user_order_list

from ..binance.utils import *

class binance(iwebsocket, CcxtDelegator, Thread):
    exchange = 'binance'
    def __init__(self, apiKey: str='', secret: str='') -> None:
        Thread.__init__(self)
        CcxtDelegator.__init__(self, 'binance', {'apiKey': apiKey, 'secret': secret})
        self.channel = "wss://stream.binance.com:9443/ws"
        self._key = apiKey
        self._secret = secret
        self.message_queue: Queue = Queue()
        self.ws = websocket.WebSocketApp(
            self.channel,
            on_message=self.on_message,
            on_open=self.on_open,
            on_error=self.on_error,
        )
        self.orderbook = {}
        self.user_order_list = user_order_list(order_list={})

    def on_message(self, ws: websocket.WebSocketApp, message: str) -> None:
        messages = json.loads(message)
        self.auth(messages)
        if not messages.get('e'):
            return
        
        if messages['e'] == 'depthUpdate':
            symbol = messages['s']
            orderbook_dict = to_orderbook_snapshot(messages)
            if symbol not in self.orderbook.keys():
                self.orderbook[symbol] = orderbook(
                    exchange='binace',
                    symbol=symbol,
                    asks=orderbook_dict['asks'],
                    bids=orderbook_dict['bids'])
            else:
                for id_, q in orderbook_dict['asks'].items():
                    self.orderbook[symbol].insert_ask(id=id_, q=q)
                for id_, q in orderbook_dict['bids'].items():
                    self.orderbook[symbol].insert_bid(id=id_, q=q)
            delete_order_ids = []
            for id_, q in self.orderbook[symbol].asks.items():
                if not q.amount:
                    delete_order_ids.append(id_)
            for id_, q in self.orderbook[symbol].bids.items():
                if not q.amount:
                    delete_order_ids.append(id_)
            for id_ in delete_order_ids:
                self.orderbook[symbol].delete_order(id=id_)
                
            # self.message_queue.put(
            #     self.orderbook[symbol].to_simple_orderbook()
            # )

        if messages['e'] == 'trade':
            self.message_queue.put(to_execution(messages))

    def auth(self, message: dict) -> None:
        pass

    def on_open(self, ws: websocket.WebSocketApp) -> None:
        return

    def run(self) -> None:
        self.ws.run_forever(ping_interval=60)

    def close(self) -> None:
        self.ws.close()

    def convert_message(self, message: dict) -> dict:
        return message

    def subscribe_execution(self, symbol: str) -> None:
        message = {
            "method": "SUBSCRIBE",
            "params": [f'{convert_symbol(symbol)}@trade'],
            "id": 1
        }
        self.ws.send(json.dumps(message))

    def subscribe_user_execution(self, symbol: str) -> None:
       pass

    def subscribe_orderbook(self, symbol: str) -> None:
        message = {
            "method": "SUBSCRIBE",
            "params": [f'{convert_symbol(symbol)}@depth'],
            "id": 1
        }
        self.ws.send(json.dumps(message))

    def subscribe_user_order(self, funding_currency: str) -> None:
        pass
