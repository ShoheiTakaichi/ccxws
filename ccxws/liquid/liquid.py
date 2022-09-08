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

from ..liquid.utils import *

class liquid(iwebsocket, CcxtDelegator, Thread):
    exchange = 'liquid'
    def __init__(self, apiKey: str='', secret: str='') -> None:
        Thread.__init__(self)
        CcxtDelegator.__init__(self, 'liquid', {'apiKey': apiKey, 'secret': secret})
        self.channel = "wss://tap.liquid.com/app/LiquidTapClient"
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
        self.is_auth = False

    def on_message(self, ws: websocket.WebSocketApp, message: str) -> None:
        messages = json.loads(message)
        self.auth(messages)
        if 'channel' not in messages.keys():
            return
        if 'price_ladders_cash' in messages['channel'] and messages['data']:
            symbol = messages['channel'].split('_')[3]
            orderbook_dict = to_orderbook_snapshot(messages)
            if symbol not in self.orderbook.keys():
                self.orderbook[symbol] = orderbook(
                    exchange = 'liquid',
                    symbol = symbol,
                    asks = orderbook_dict['asks'],
                    bids = orderbook_dict['bids'])
            else:
                asks = orderbook_dict['asks'] if len(orderbook_dict['asks'])>0 else self.orderbook[symbol].asks
                bids = orderbook_dict['bids'] if len(orderbook_dict['bids'])>0 else self.orderbook[symbol].bids
                self.orderbook[symbol].from_snapshot(
                    asks = asks,
                    bids = bids)

            self.message_queue.put(
                self.orderbook[symbol].to_simple_orderbook()
            )

        if 'execution_details_cash' == messages['channel'][0:22] and messages['data']:
            symbol = messages['channel'].split('_')[2]
            self.message_queue.put(to_execution(symbol, json.loads(messages['data'])))

        if 'user_executions_cash' == messages['channel'][0:20] and messages['data']:
            symbol = messages['channel'].split('_')[3]
            self.message_queue.put(
                to_user_execution(
                    symbol=symbol,
                    data=json.loads(messages['data'])
                )
            )

        if 'user_account' == messages['channel'][0:12] and 'orders' == messages['channel'][-6:] and messages['data']:
            symbol = messages['channel'].split('_')[2]
            data = json.loads(messages['data'])
            if data['status'] == 'cancelled' and str(data['id']) in self.user_order_list.order_list.keys():
                self.user_order_list.order_list.pop(str(data['id']))
            if data['status'] == 'filled' and str(data['id']) in self.user_order_list.order_list.keys():
                self.user_order_list.order_list.pop(str(data['id']))
            if data['status'] == 'live':
                self.user_order_list.order_list[str(data['id'])] = to_user_order(data)
            self.message_queue.put(self.user_order_list.to_simple_user_order_list())
            # print(messages)

    def auth(self, message: dict) -> None:
        if message["event"] == 'quoine:auth_success':
            self.is_auth = True
        if message["event"] == 'quoine:auth_failure':
            time.sleep(1)
        if message["event"] == "pusher:connection_established" or message["event"] == "quoine:auth_failure":
            params = {
                "event": "quoine:auth_request",
                "data": {
                    "path": "/realtime",
                    "headers": {
                        "X-Quoine-Auth": jwt.encode(
                            {
                                "token_id": self._key,
                                "path": "/realtime",
                                "nonce": int(time.time() * 1000000),
                            },
                            self._secret,
                        )
                    },
                },
            }
            self.ws.send(json.dumps(params))


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
            "event": "pusher:subscribe",
            "data": {"channel": f"execution_details_cash_{convert_symbol(symbol)}"}
        }
        self.ws.send(json.dumps(message))

    def subscribe_user_execution(self, symbol: str) -> None:
        message = {
            "event": "pusher:subscribe",
            "data": {"channel": f"user_executions_cash_{convert_symbol(symbol)}"},
        }
        self.ws.send(json.dumps(message))

    def subscribe_orderbook(self, symbol: str) -> None:
        print(convert_symbol(symbol))
        message = {
            "event": "pusher:subscribe",
            "data": {"channel": f"price_ladders_cash_{convert_symbol(symbol) }_buy"},
        }
        self.ws.send(json.dumps(message))
        message = {
            "event": "pusher:subscribe",
            "data": {"channel": f"price_ladders_cash_{convert_symbol(symbol) }_sell"},
        }
        self.ws.send(json.dumps(message))

    def subscribe_user_order(self, funding_currency: str) -> None:
        message = {
            "event": "pusher:subscribe",
            "data": {"channel": f"user_account_{funding_currency.lower()}_orders"},
        }
        self.ws.send(json.dumps(message))
