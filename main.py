from binance.client import Client
from flask import Flask
import time
import json

api_key = 'zYrcVXuv66HdQhnK6SYGaFPEJzgtB2mN9M69ruFIvIfyPYkID6EcM5Nf4Ik4qXsD'
secret_key = 'W3WpegHdDkdeZtLaoxdsWXl8HEeZzURxH1YdY2ID5ba5DxvneJThgwg79VJgAdZE'
app = Flask(__name__)

client = Client(api_key, secret_key)

client.API_URL = 'https://fapi.binance.com/'
@app.route('/balance')
def Balance():
    balances = client.futures_account_balance()
    for balance in balances:
        if balance['asset'] == 'USDT':
            USDT = balance['balance']
            return USDT
    return 0

@app.route('/action', methods=['POST'])
def Action():
    data = request.get_json()
    print(data)
    if 'buy' in str(data) or 'BUY' in str(data) or 'Buy' in str(data):
        client.futures_create_order(symbol='ETHUSDT', side='BUY', type='MARKET', quantity=0.025)
    else:
        client.futures_create_order(symbol='ETHUSDT', side='SELL', type='MARKET', quantity=0.025)

    return action

def OpenOrders():
    orders = client.futures_get_open_orders()
    return orders

#print(OpenOrders())
#CreateOrder()
app.run(host='127.0.0.1', port=80)
