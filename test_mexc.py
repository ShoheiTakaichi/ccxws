import ccxws
from time import sleep
from pprint import pprint


api = ''
secret = ''


client = ccxws.mexc(apiKey = api, secret = secret)

client.start()
sleep(1)

client.subscribe_execution('BTC/USDT')
# client.auth()


while True:
    message = client.message_queue.get()
    event_name = type(message).__name__
    print(event_name)
    if event_name == "simple_user_order_list":
        pprint(message)
    if event_name == "user_execution":
        pprint(message)
    # print(message)