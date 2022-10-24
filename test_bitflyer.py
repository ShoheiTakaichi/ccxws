import ccxws
from time import sleep
from pprint import pprint

api = ''
secret = ''


client = ccxws.bitflyer(apiKey = api, secret = secret)

client.start()

sleep(1)
# client.subscribe_orderbook('BTC_JPY')
client.subscribe_execution('BTC/JPY')

client.subscribe_user_order()

while True:
    message = client.message_queue.get()
    print(message)
