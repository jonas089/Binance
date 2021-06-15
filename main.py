from binance.client import Client
from flask import Flask
import time
import json

try:
    open('history.dat', 'x')
except Exception as exists:
    pass
api_key = 'zYrcVXuv66HdQhnK6SYGaFPEJzgtB2mN9M69ruFIvIfyPYkID6EcM5Nf4Ik4qXsD'
secret_key = 'W3WpegHdDkdeZtLaoxdsWXl8HEeZzURxH1YdY2ID5ba5DxvneJThgwg79VJgAdZE'
app = Flask(__name__)
client = Client(api_key, secret_key)
client.API_URL = 'https://fapi.binance.com/'
#@app.route('/balance')
def Balance():
    balances = client.futures_account_balance()
    for balance in balances:
        if balance['asset'] == 'USDT':
            USDT = balance['balance']
            return float(USDT)
    return 0

def Price():
    tickers = client.futures_coin_symbol_ticker(symbol='ETHUSD_PERP')
    #print(tickers)
    return float(tickers[0]['price'])


@app.route('/action', methods=['POST'])
def Action():
    amount = str(Balance()/Price())
    if len(amount) > 5:
        amount = amount[:5]
    print('Max_Amount: ' + str(amount))
    data = request.get_json()
    print(data)
    if 'buy' in str(data):
        client.futures_create_order(symbol='ETHUSDT', side='BUY', type='MARKET', quantity=float(amount))
        with open('history.dat', 'w') as history:
            history.write(str(amount))
    elif 'sell' in str(data):
        with open('history.dat', 'r') as history:
            positioned_amount = float(history.read())
        client.futures_create_order(symbol='ETHUSDT', side='SELL', type='MARKET', quantity=positioned_amount)
    else:
        print('Warning: ' + str(data))
    return action

def OpenOrders():
    orders = client.futures_get_open_orders()
    return orders

#print(OpenOrders())
#CreateOrder()
print(Price())
#app.run(host='127.0.0.1', port=80)
