from binance.client import Client
from flask import Flask, request
import time
import json
import pickle

leverages = {'ADA':1, 'DOT':2, 'ETH':4, 'LTC':1, 'XMR':7}
try:
    open('history.dat', 'x')
    open('first.dat', 'x')
except Exception as exists:
    pass
with open('first.dat', 'wb') as first:
    initial_data = {'ADA':True, 'DOT':True, 'ETH':True, 'LTC':True, 'XMR':True}
    pickle.dump(initial_data, first)
with open('history.dat', 'wb') as history:
    initial_data = {'ADA':0, 'DOT':0, 'ETH':0, 'LTC':0, 'XMR':0}
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
    data = request.json['action']
    print(data)
    ticker = request.json['ticker']

    amount = str(Balance()/Price(ticker)) * 0.5
    if len(amount) > 5:
        amount = amount[:5]
    print('Max_Amount: ' + str(amount))
    issafe = False
    if 'sell' in str(data):
        with open('first.dat', 'rb') as first:
            is_first = pickle.load(first)
            if is_first[ticker] ==  True:
                is_first[ticker] = False
                issafe = True
        if issafe == True:
            with open('first.dat', 'wb') as first:
                pickle.dump(is_first, first)
            return 0


    if str(data) == 'buy':
        with open('history.dat', 'rb') as history:
            history_bu = pickle.load(history)
        with open('history.dat', 'wb') as history:
            history_bu[ticker] = float(amount)
            pickle.dump(history_bu, history)
        with open('first.dat', 'rb') as first:
            is_first = pickle.load(first)
            is_first[ticker] = False
        with open('first.dat', 'wb') as first:
            pickle.dump(is_first, first)
        return client.futures_create_order(symbol=(ticker+'USDT'), side='BUY', type='MARKET', quantity=(float(amount) * leverages[ticker]))

    elif str(data) == 'sell':
        with open('history.dat', 'rb') as history:
            positioned_amount = pickle.load(history)[ticker]
        return client.futures_create_order(symbol=(ticker+'USDT'), side='SELL', type='MARKET', quantity=(positioned_amount * leverages[ticker]))
    else:
        print('Warning: ' + str(data))
    return 0

def OpenOrders():
    orders = client.futures_get_open_orders()
    return orders

#print(OpenOrders())
#CreateOrder()
#print(Price())
app.run(host='217.160.63.112', port=80)
