from pprint import pprint
from time import sleep

from ccxws import bitget

api = ""
secret = ""
passphrase = ""

client = bitget(apikey=api, secret=secret, passphrase=passphrase)

client.start()
sleep(1)

client.subscribe_orderbook("BTC/JPY")
# client.subscribe_user_execution("gxtusdt")
client.subscribe_execution("BTC/JPY")
# client.subscribe_user_order("jpy")

while True:
    event = client.message_queue.get()
    pprint(event)
