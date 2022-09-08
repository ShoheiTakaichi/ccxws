import abc
import websocket
import traceback


class iwebsocket(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def on_open(self, ws: websocket.WebSocketApp) -> None:
        raise NotImplementedError()

    @abc.abstractmethod
    def on_message(self, ws: websocket.WebSocketApp, message: str) -> None:
        raise NotImplementedError()

    @abc.abstractmethod
    def close(self) -> None:
        raise NotImplementedError()

    @abc.abstractmethod
    def subscribe_orderbook(self, symbol: str) -> None:
        raise NotImplementedError()

    @abc.abstractmethod
    def subscribe_execution(self, symbol: str) -> None:
        raise NotImplementedError()

    @abc.abstractmethod
    def subscribe_user_execution(self, symbol: str) -> None:
        raise NotImplementedError()

    def on_error(self, ws: websocket.WebSocketApp, error) -> None:
        print(traceback.format_exc())