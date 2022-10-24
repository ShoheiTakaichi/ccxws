from pprint import pprint
from time import sleep

from ccxws import liquid

api = ''
secret = ''

client = liquid(apiKey=api, secret=secret)

client.start()
sleep(1)

client.subscribe_orderbook('BTC/JPY')
client.subscribe_execution('BTC/JPY')
# client.subscribe_user_order('jpy')

while True:
    event = client.message_queue.get()
    pprint(event)
