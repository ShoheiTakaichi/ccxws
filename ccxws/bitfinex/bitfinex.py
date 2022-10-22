import websocket
import hashlib
import hmac
import json
import time
from threading import Thread
from queue import Queue
from loguru import logger

from ..iwebsocket import iwebsocket
from ..ccxt_delegator import CcxtDelegator

from ..models import user_execution, orderbook, quote, user_order_list

from ..bitfinex.utils import *


class bitfinex(iwebsocket, CcxtDelegator, Thread):
    exchange = 'bitfinex'

    def __init__(self, apiKey: str = '', secret: str = '') -> None:
        Thread.__init__(self)
        CcxtDelegator.__init__(self, 'bitfinex', {'apiKey': apiKey, 'secret': secret})
        self.channel = "wss://api.bitfinex.com/ws/2"
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
        self.balance = balance()
        self.user_order_list = user_order_list(order_list={})
        self.chanIds = {}  # first message of a channel

        self.auth_event_subscription = {
            # 'user_order': False,
            # 'user_execution': False
        }

    def on_message(self, ws: websocket.WebSocketApp, message: str) -> None:
        messages = json.loads(message)
        # logger.info(messages)

        if type(messages) == dict and messages.get('chanId') is not None:
            self.chanIds[messages.get('chanId')] = messages

        if type(messages) == list:
            if messages[0] == 0:
                # WEBSOCKET AUTHENTICATED CHANNELS
                # if message[1] 
                if messages[1] == 'ws':
                    self.balance.from_bitfinex(messages[2])

                elif messages[1] == 'wu':
                    self.balance.update_bitfinex(messages[2])

                # elif messages[1] == 'bu':
                #     continue

                # 'os' (order snapshot)
                # 'on' (order new)
                # 'ou' (order update)
                # 'oc' (order cancel (canceled or fully executed))
                elif messages[1] == 'oc' or messages[1] == 'ou' or messages[1] == 'on' or messages[1] == 'os':
                    if messages[1] == 'oc':
                        self.user_order_list.order_list.pop(str(messages[2][0]))
                    if messages[1] == 'on' or messages[2] == 'ou':
                        self.user_order_list.order_list[str(messages[2][0])] = to_user_order(messages[2][0])
                    if messages[1] == 'os':
                        self.user_order_list.order_list = {}
                        for d in messages[2]:
                            self.user_order_list.order_list[str(d[2][0])] = to_user_order(d[2][0])
                    self.message_queue.put(self.user_order_list.to_simple_user_order_list())

                elif messages[1] == 'te':
                    self.message_queue.put(
                        to_user_execution(
                            symbol=messages[2][1][1:],
                            data=messages[2]
                        )
                    )

                elif messages[1] == 'tu':
                    self.message_queue.put(
                        to_user_execution(
                            symbol=messages[2][1][1:],
                            data=messages[2]
                        )
                    )

                # elif messages[1] == 'n':
                #     ## do some magic

                # elif messages[1] == 'hb':
                #     ## do some magic

                # else:
                #     print(messages)

            channel = self.chanIds[messages[0]]
            if channel.get('channel') == 'book':
                symbol = channel['symbol'][1:]
                if len(messages[1]) > 3:
                    orderbook_dict = to_orderbook_snapshot(messages[1])
                    if symbol not in self.orderbook.keys():
                        self.orderbook[symbol] = orderbook(
                            exchange='bitfinex',
                            symbol=symbol,
                            asks=orderbook_dict['asks'],
                            bids=orderbook_dict['bids'])
                    else:
                        self.orderbook[symbol].from_snapshot(
                            asks=orderbook_dict['asks'],
                            bids=orderbook_dict['bids'])

                if len(messages[1]) == 3:
                    if messages[1][1] == 0:
                        self.orderbook[symbol].delete_order(messages[1][0])
                    if messages[1][1] != 0:
                        if messages[1][2] > 0:
                            self.orderbook[symbol].insert_bid(
                                id=messages[1][0],
                                q=quote(
                                    price=messages[1][1],
                                    amount=messages[1][2]
                                )
                            )
                        if messages[1][2] < 0:
                            self.orderbook[symbol].insert_ask(
                                id=messages[1][0],
                                q=quote(
                                    price=messages[1][1],
                                    amount=-messages[1][2]
                                )
                            )
                self.message_queue.put(
                    self.orderbook[symbol].to_simple_orderbook()
                )

            if channel.get('channel') == 'trades':
                if messages[1] == 'te':
                    symbol = channel['symbol'][1:]
                    self.message_queue.put(to_execution(symbol, messages[2]))

    def auth(self) -> None:
        nonce = str(int(time.time() * 1000000))
        auth_string = 'AUTH' + nonce
        auth_sig = hmac.new(self._secret.encode(), auth_string.encode(),
                            hashlib.sha384).hexdigest()
        payload = {
            'event': 'auth',
            'apiKey': self._key,
            'authSig': auth_sig,
            'authPayload': auth_string,
            'authNonce': nonce,
            'dms': 4,
            # 'filter': ['balance']
        }
        self.ws.send(json.dumps(payload))
        return

    def on_open(self, ws: websocket.WebSocketApp) -> None:
        self.auth()
        return

    def on_error(self, ws: websocket.WebSocketApp, err) -> None:
        logger.info(err)

    def run(self) -> None:
        self.ws.run_forever(ping_interval=60)

    def close(self) -> None:
        self.ws.close()

    def convert_message(self, message: dict) -> dict:
        return message

    def subscribe_execution(self, symbol: str) -> None:
        message = {
            'event': 'subscribe',
            'channel': 'trades',
            'symbol': 't' + convert_symbol(symbol)
        }
        self.ws.send(json.dumps(message))

    def subscribe_user_execution(self, symbol: str) -> None:
        self.auth_event_subscription['user_execution'] = True

    def subscribe_user_order(self, symbol: str) -> None:
        self.auth_event_subscription['user_order'] = True

    def subscribe_orderbook(self, symbol: str) -> None:
        message = {
            "event": "subscribe",
            "channel": "book",
            "prec": 'R0',
            "symbol": "t" + convert_symbol(symbol)
        }
        self.ws.send(json.dumps(message))

    # def create_order(self, symbol, side, amount, price):
    #     cid = int(round(time.time() * 1000))
    #     if side == 'sell':
    #         amount *= -1
    #     order_details = {
    #         # 'gid': 0,
    #         'cid': cid,
    #         'type': 'EXCHANGE LIMIT',
    #         'symbol': symbol,
    #         'amount': str(amount),
    #         'price' : str(price),
    #     }
    #     msg = [
    #         0,
    #         'on',
    #         None,
    #         order_details
    #     ]
    #     pprint(json.dumps(msg))
    #     self.ws.send(json.dumps(msg))
