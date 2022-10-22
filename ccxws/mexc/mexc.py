import hashlib
import hmac
import json
import time
from queue import Queue
from threading import Thread
import ccxt
import jwt
import websocket
from pprint import pprint

from ccxws.iwebsocket import iwebsocket
from ccxws.ccxt_delegator import CcxtDelegator

from ..models import orderbook, quote, user_order_list

from ..mexc.utils import *


# https://mxcdevelop.github.io/apidocs/spot_v2_en/#limited-depth

class mexc(iwebsocket, CcxtDelegator, Thread):
    def __init__(self, apiKey: str, secret: str) -> None:
        Thread.__init__(self)
        CcxtDelegator.__init__(self, 'mexc', {'apiKey': apiKey, 'secret': secret})
        self.apiKey = apiKey
        self.secret = secret
        self.channel = "wss://wbs.mexc.com/raw/ws"
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
        message = json.loads(message)
        if message['channel'] == 'push.limit.depth':
            orderbook_dict = to_orderbook_snapshot(message['data'])
            symbol = convert_symbol(message['symbol'], True)
            if symbol not in self.orderbook.keys():
                self.orderbook[symbol] = orderbook(
                    exchange='mexc',
                    symbol=symbol,
                    asks=orderbook_dict['asks'],
                    bids=orderbook_dict['bids'])
            else:
                self.orderbook[symbol].from_snapshot(
                    asks=orderbook_dict['asks'],
                    bids=orderbook_dict['bids'])
            self.message_queue.put(
                self.orderbook[symbol].to_simple_orderbook()
            )
        elif message['channel'] == 'push.symbol':
            symbol = convert_symbol(message['symbol'], True)
            if message['data'].get('deals'):
                for data in message['data']['deals']:
                    self.message_queue.put(to_execution(symbol, data))
        elif message['channel'] == 'push.personal.order':
            symbol = convert_symbol(message['symbol'], True)
            status = message['data']['status']
            id = message['data']['id']
            if status == 1:  # new
                self.user_order_list.order_list[id] = to_user_order(symbol, message['data'])
            if status == 3:  # partially filled
                self.user_order_list.order_list[id] = to_user_order(symbol, message['data'])
            if status == 2:  # filled
                self.user_order_list.order_list.pop(id)
            if status == 4:  # order canceled
                self.user_order_list.order_list.pop(id)
            if status == 5:  # partially filled and canceled
                self.user_order_list.order_list.pop(id)
            self.message_queue.put(self.user_order_list.to_simple_user_order_list())
        elif message['channel'] == 'push.personal.deals':
            symbol = convert_symbol(message['symbol'], True)
            self.message_queue.put(
                to_user_execution(
                    symbol,
                    message['data']
                )
            )
        else:
            pprint(message)

    def auth(self) -> None:
        timestamp = str(int(time.time() * 1000))
        signature = hmac.new(self.secret.encode(), f"{self.apiKey}{timestamp}".encode(), hashlib.sha256).hexdigest()
        signature = hashlib.md5(
            "api_key={}&op=sub.personal.deals&req_time={}&api_secret={}".format(self.apiKey, timestamp, self.secret)
            .encode()
        ).hexdigest()
        message = {
            "op": "sub.personal.deals",
            "api_key": self.apiKey,
            "sign": signature,
            "req_time": timestamp
        }
        self.ws.send(json.dumps(message))
        signature = hmac.new(self.secret.encode(), f"{self.apiKey}{timestamp}".encode(), hashlib.sha256).hexdigest()
        signature = hashlib.md5(
            "api_key={}&op=sub.personal&req_time={}&api_secret={}".format(self.apiKey, timestamp, self.secret)
            .encode()
        ).hexdigest()
        message = {
            "op": "sub.personal",
            "api_key": self.apiKey,
            "sign": signature,
            "req_time": timestamp
        }
        self.ws.send(json.dumps(message))
        return

    def on_open(self, ws: websocket.WebSocketApp) -> None:
        self.auth()
        # self.subscribe_orderbook("GXT_USDT")
        # self.subscribe_execution("GXT_USDT")
        return

    def subscribe_orderbook(self, symbol: str) -> None:
        message = {"op": "sub.limit.depth", "symbol": convert_symbol(symbol), "depth": 20}
        self.ws.send(json.dumps(message))
        return

    def subscribe_execution(self, symbol: str) -> None:
        message = {"op": "sub.symbol", "symbol": convert_symbol(symbol)}
        self.ws.send(json.dumps(message))
        return

    def subscribe_user_execution(self, symbol: str) -> None:
        print('included in auth')
        return

    def on_error(self, ws: websocket.WebSocketApp, error: str) -> None:
        print(error)

    def run(self) -> None:
        self.ws.run_forever(ping_interval=60)

    def close(self) -> None:
        self.ws.close()

