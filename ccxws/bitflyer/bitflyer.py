
import json
import time
from queue import Queue
from threading import Thread
from pprint import pprint
import websocket
import hmac
from hashlib import sha256
from secrets import token_hex
import jwt
import websocket

from ccxws.iwebsocket import iwebsocket
from ccxws.ccxt_delegator import CcxtDelegator
from ccxws.models import orderbook, quote
from .utils import *

class bitflyer(iwebsocket, CcxtDelegator, Thread):
    exchange = 'bitflyer'
    def __init__(self, apiKey: str='', secret: str='') -> None:
        Thread.__init__(self)
        CcxtDelegator.__init__(self, 'bitflyer', {'apiKey': apiKey, 'secret': secret})
        self.channel = "wss://ws.lightstream.bitflyer.com/json-rpc"
        self._key = apiKey
        self._secret = secret
        self._JSONRPC_ID_AUTH = 1
        self.message_queue: Queue = Queue()
        self.ws = websocket.WebSocketApp(
            self.channel,
            on_message=self.on_message,
            on_open=self.on_open,
            on_error=self.on_error,
        )
        self.orderbook = {}
        self.is_auth = False

    def on_message(self, ws: websocket.WebSocketApp, message: str) -> None:
        messages = json.loads(message)
        if message == '{"jsonrpc":"2.0","id":1,"result":true}':
            self.is_auth = True
        if 'method' in messages.keys():
            if messages['method'] == 'channelMessage':
                if messages['params']['channel'][0:16] == 'lightning_board_' and messages['params']['channel'][0:25] != 'lightning_board_snapshot_':
                    symbol = messages['params']['channel'][16:]
                    asks = messages['params']['message']['asks']
                    bids = messages['params']['message']['bids']
                    for order in asks:
                        if order['size'] == 0:
                            self.orderbook[symbol].delete_order(order['price'])
                        else:
                            self.orderbook[symbol].insert_ask(id=order['price'], q=quote(price=order['price'],amount=order['size']))
                    for order in bids:
                        if order['size'] == 0:
                            self.orderbook[symbol].delete_order(order['price'])
                        else:
                            self.orderbook[symbol].insert_bid(id=order['price'], q=quote(price=order['price'],amount=order['size']))
                    self.message_queue.put(self.orderbook[symbol].to_simple_orderbook())
                if messages['params']['channel'][0:25] == 'lightning_board_snapshot_':
                    symbol = messages['params']['channel'][25:]
                    orderbook_dict = to_orderbook_snapshot(messages['params']['message'])
                    if symbol not in self.orderbook.keys():
                        self.orderbook[symbol] = orderbook(
                            exchange = 'bitflyer',
                            symbol = symbol,
                            asks = orderbook_dict['asks'],
                            bids = orderbook_dict['bids'])
                    else:
                        asks = orderbook_dict['asks']
                        bids = orderbook_dict['bids']
                        self.orderbook[symbol].from_snapshot(
                            asks = asks,
                            bids = bids)
                    self.message_queue.put(self.orderbook[symbol].to_simple_orderbook())
                if messages['params']['channel'][0:21] == 'lightning_executions_':
                    symbol = messages['params']['channel'][21:]
            else:
                pprint(messages)
        else:
            pprint(messages)



    def auth(self):
        now = int(time.time())
        nonce = token_hex(16)
        sign = hmac.new(self._secret.encode('utf-8'), ''.join([str(now), nonce]).encode('utf-8'), sha256).hexdigest()
        params = {
            'method': 'auth',
            'params': {
                'api_key': self._key,
                'timestamp': now,
                'nonce': nonce,
                'signature': sign
            }
            ,
            'id': self._JSONRPC_ID_AUTH
        }
        self.ws.send(json.dumps(params))


    def on_open(self, ws: websocket.WebSocketApp) -> None:
        self.auth()
        return

    def on_error(self, ws: websocket.WebSocketApp, error: str) -> None:
        # print('error desuyo')
        # print(error)
        return

    def run(self) -> None:
        self.ws.run_forever(ping_interval=60)

    def close(self) -> None:
        self.ws.close()

    def convert_message(self, message: dict) -> dict:
        return message

    def subscribe_execution(self, symbol: str) -> None:
        message = {
            "method": "subscribe",
            "params": {"channel": f"lightning_executions_{convert_symbol(symbol)}"},
        }
        self.ws.send(json.dumps(message))

    def subscribe_user_execution(self, symbol: str) -> None:
        message = {
            "event": "pusher:subscribe",
            "data": {"channel": f"user_executions_cash_{convert_symbol(symbol)}"},
        }
        self.ws.send(json.dumps(message))

    def subscribe_orderbook(self, symbol: str) -> None:
        message = {
            "method": "subscribe",
            "params": {"channel": f"lightning_board_snapshot_{convert_symbol(symbol)}"},
        }
        self.ws.send(json.dumps(message))
        message = {
            "method": "subscribe",
            "params": {"channel": f"lightning_board_{convert_symbol(symbol)}"},
        }
        self.ws.send(json.dumps(message))

    def subscribe_user_order(self) -> None:
        message = {
            "method": "subscribe",
            "params": {"channel": "child_order_events"},
        }
        self.ws.send(json.dumps(message))
