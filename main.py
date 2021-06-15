from binance.client import Client
from flask import Flask
import time
import json
import pickle

try:
    open('history.dat', 'x')
except Exception as exists:
    pass
with open('history.dat', 'wb') as history:
    initial_data = [{'ADA':0}, {'DOT':0}, {'ETH':0}, {'LTC':0}]
    pickle.dump(initial_data, history)
api_key = 'w5WslwajZVtl45kJdSsU6aTDW55ZmMyn9vy7txcJnGTxmBzs92MV7hTnMCYDTyVE'
secret_key = 'sYOZrlfkgcRpteYXUhYSvEmrngpwCu6TIdxhKYTXqMXzXJEQ1NCiFYW1AwD1MUvv'
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

def Price(ticker):
    tickers = client.futures_coin_symbol_ticker(symbol=(ticker+'USD_PERP'))
    #print(tickers)
    return float(tickers[0]['price'])


@app.route('/action', methods=['POST'])
def Action():
    data = request.get_json()
    print(data)
    ticker = data[:3]

    amount = str(Balance()/Price(ticker))
    if len(amount) > 5:
        amount = amount[:5]
    print('Max_Amount: ' + str(amount))

    if 'buy' in str(data) and Balance() > 1:
        client.futures_create_order(symbol=(ticker+'USDT'), side='BUY', type='MARKET', quantity=float(amount))
        with open('history.dat', 'rb') as history:
            history_bu = pickle.load(history)
        with open('history.dat', 'wb') as history:
            history_bu[ticker] = float(amount)
            pickle.dump(history_bu, history)
    elif 'sell' in str(data):
        with open('history.dat', 'rb') as history:
            positioned_amount = pickle.load(history)[ticker]
        client.futures_create_order(symbol=(ticker+'USDT'), side='SELL', type='MARKET', quantity=positioned_amount)
    else:
        print('Warning: ' + str(data))
    return action

def OpenOrders():
    orders = client.futures_get_open_orders()
    return orders

#print(OpenOrders())
#CreateOrder()
#print(Price())
app.run(host='217.160.63.112', port=80)
