import ccxws
from time import sleep
from pprint import pprint
import json

api = ''
secret = ''


client = ccxws.bitfinex(apiKey = api, secret = secret)
# client = ccxws.bitfinex_dict(apiKey = api, secret = secret)

client.start()
sleep(1)

# client.subscribe_execution('BTC/USDT')
client.auth()

# print(
#     client.fetch_balance()
# )


# def new_order_market(symbol, amount, price):
#     global ws
#     cid = int(round(time() * 1000))
#     order_details = {
#         'gid': 0,
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
#     client.ws.send(json.dumps(msg))
# sleep(3)
# new_order_market('tBTCUSD', 0.005, 20000)
# #



while True:
    message = client.message_queue.get()
    print(message)