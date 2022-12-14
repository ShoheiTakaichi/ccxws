import ccxt
from time import time
from .models import *

class CcxtDelegator():
    exchange: str
    def __init__(self, exchange, key):
        self.exchange = exchange
        if exchange == 'liquid':
            self.__ccxt = ccxt.liquid(key)

        if exchange == 'bitfinex':
            self.__ccxt = ccxt.bitfinex(key)

        if exchange == 'mexc':
            self.__ccxt = ccxt.mexc(key)
        
        if exchange == 'binance':
            self.__ccxt = ccxt.binance(key)

        if exchange == 'bitflyer':
            self.__ccxt = ccxt.bitflyer(key)

    def create_order(self, symbol, side, amount, price):
        return self.__ccxt.create_order(
            symbol=self._convert_symbol(symbol),
            side=side,
            amount=amount,
            price=price,
            type='limit')

    def create_market_order(self, symbol, side, amount):
        return self.__ccxt.create_order(
            symbol=self._convert_symbol(symbol),
            side=side,
            amount=amount,
            type='market')

    def cancel_order(self, symbol, id):
        return self.__ccxt.cancel_order(id=id, symbol=self._convert_symbol(symbol))

    def edit_order(self, id, symbol, side, amount, price):
        return self.__ccxt.edit_order(id, self._convert_symbol(symbol), 'limit', side, amount, price)

    def fetch_balance(self) -> balance:
        if self.exchange != 'bitflyer':
            try:
                res = self.__ccxt.fetch_balance()
                b = balance.from_ccxt(self.exchange, res)
                return b
            except Exception as e:
                print(e)
        if self.exchange == 'bitflyer':
            try:
                res = self.__ccxt.fetch_balance()
                positions = self.__ccxt.private_get_getpositions(params = { "product_code" : "FX_BTC_JPY" })
                collateral = self.__ccxt.private_get_getcollateral()
                res['JPY_FX'] = {
                    'free': float(collateral['collateral']) - float(collateral['require_collateral']),
                    'used': collateral['require_collateral']
                }
                btc_fx_position = 0
                for position in positions:
                    if position['side'] == 'SELL':
                        btc_fx_position -= float(position['size'])
                    if position['side'] == 'BUY':
                        btc_fx_position += float(position['size'])
                res['BTC_FX'] = {
                    'free': btc_fx_position,
                    'used': 0
                }
                b = balance.from_ccxt(self.exchange, res)
                return b
            except Exception as e:
                print(e)

    def fetch_open_orders(self, symbol):
        return self.__ccxt.fetch_open_orders(symbol=self._convert_symbol(symbol))

    def fetch_ohlcv(self, symbol, timeframe = '1m', limit=1000):
        if timeframe == '1m':
            since = int((time() - limit*60) * 1000)
            return self.__ccxt.fetch_ohlcv(symbol=self._convert_symbol(symbol), timeframe=timeframe,limit=limit, since=since)
        if timeframe == '5m':
            since = int((time() - limit*300) * 1000)
            return self.__ccxt.fetch_ohlcv(symbol=self._convert_symbol(symbol), timeframe=timeframe,limit=limit, since=since)
        if timeframe == '1h':
            since = int((time() - limit*60*60) * 1000)
            return self.__ccxt.fetch_ohlcv(symbol=self._convert_symbol(symbol), timeframe=timeframe,limit=limit, since=since)
        if timeframe == '1d':
            since = int((time() - limit*60*60*24) * 1000)
            return self.__ccxt.fetch_ohlcv(symbol=self._convert_symbol(symbol), timeframe=timeframe,limit=limit, since=since)


    def fetch_order_book(self, symbol):
        return self.__ccxt.fetch_order_book(symbol=self._convert_symbol(symbol))

    def _convert_symbol(self, symbol):
        if self.exchange == 'bitflyer':
            return symbol.replace('/','_')
        return symbol