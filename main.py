from binance.client import Client
from flask import Flask, request
import time
import json
import pickle
import os
# (RE)Create Files
files = ['history.dat', 'first.dat', 'positions.dat', 'leverages.dat', 'precisions.dat', 'strategies.dat', 'log.txt', 'tradelog.txt']
for f in range(0, len(files)):
    try:
        os.remove(files[f])
    except Exception as nofile:
        pass
    try:
        open(files[f], 'x')
    except Exception as exists:
        print('Warning! Files exist.')

# Instantiate
with open('first.dat', 'wb') as first:
    initial_data = {'ADA':True, 'DOT':True, 'ETH':True} #'XMR':True} XMR - Futures Price not supported by API
    pickle.dump(initial_data, first)
with open('history.dat', 'wb') as history:
    initial_data = {'ADA':0, 'DOT':0, 'ETH':0} #'XMR':0} XMR - Futures Price not supported by API
    pickle.dump(initial_data, history)
with open('positions.dat', 'wb') as pos:
    positions = {'ADA':'None', 'DOT':'None', 'ETH':'None'} #'XMR':'None'} XMR - Futures Price not supported by API
    pickle.dump(positions, pos)
with open('leverages.dat', 'wb') as lev:
    leverages = {'ADA':4, 'DOT':4, 'ETH':5} #'XMR':4} XMR - Futures Price not supported by API
    pickle.dump(leverages, lev)
with open('precisions.dat', 'wb') as pre:
    precisions = {'ADA':1, 'DOT':2, 'ETH':3}
    pickle.dump(precisions, pre)
with open('strategies.dat', 'wb') as sg:
    strategies = {'ETH':'None','ADA':'None','DOT':'None'}
with open('log.txt', 'w') as log:
    log.write('[DEBUG]: ' + '\n')
with open('tradelog.txt', 'w') as tradelog:
    log.write('[Trades]: ' + '\n')
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
    timestamp = str(time.time())
    try:
        data = request.get_json()['action']
        print(data)
        ticker = request.get_json()['ticker']
        strategy = request.get_json()['strategy']
    except Exception as FormatError:
        data = request.json['action']
        ticker = request.json['ticker']
        strategy = request.json['strategy']
    with open('precisions.dat', 'rb') as precisions:
        asset_precision = pickle.load(precisions)[ticker]

    amount = str(round((Balance()/Price(ticker))*1, asset_precision))
    print('Max_Amount: ' + str(amount))
    #issafe = False
    #if 'sell' in str(data):
        #with open('first.dat', 'rb') as first:
        #    is_first = pickle.load(first)
        #    if is_first[ticker] ==  True:
        #        is_first[ticker] = False
        #        issafe = True
        #if issafe == True:
        #    with open('first.dat', 'wb') as first:
        #        pickle.dump(is_first, first)
        #    return 0
    with open('leverages.dat', 'rb') as lev:
        leverages = pickle.load(lev)
        leverage = float(leverages[ticker])

    with open('positions.dat', 'rb') as pos:
        positions = pickle.load(pos)
        position = positions[ticker]

    with open('strategies.dat', 'rb') as sg:
        strategies = pickle.load(sg)
        current_strategy = strategies[ticker]
    if current_strategy == 'None':
        strategies[ticker] = strategy
        with open('strategies.dat', 'wb') as sg:
            pickle.dump(strategies, sg)
    elif current_strategy != strategy:
        with open('log.txt', 'r') as log:
            debug_log = log.read()
        with open('log.txt', 'w') as log:
            debug_log += '[W] Strategy ' + strategy + ' not in use!' + '\n' + 'Expected: ' + strategies[ticker] + '\n'
        return 'Strategy not in use.'
    elif current_strategy == strategy:
        strategies[ticker] = 'None'
        with open('strategies.dat', 'wb') as sg:
            pickle.dump(strategies, sg)
    if str(data) == 'buy':
        #LOG
        with open('tradelog.txt', 'r') as tradelog:
            trade_log = tradelog.read()
        with open('tradelog.txt', 'w') as tradelog:
            trade_log += '[TRADE]: ' + timestamp + ' | '  + 'Sym: ' + ticker + ' Sg: ' + strategy + ' Side: ' + 'BUY' + '\n'
            tradelog.write(trade_log)

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

        if position == 'None':
            with open('positions.dat', 'wb') as pos:
                positions[ticker] = 'Buy'
                pickle.dump(positions, pos)
        elif position == 'Sell':
            with open('positions.dat', 'wb') as pos:
                with open('history.dat', 'rb') as history:
                    positioned_amount = pickle.load(history)[ticker]

                if position == 'None':
                    with open('positions.dat', 'wb') as pos:
                        positions[ticker] = 'Sell'
                        pickle.dump(positions, pos)
                positions[ticker] = 'None'
                # Close old position and open new Long position,
                client.futures_create_order(symbol=(ticker+'USDT'), side='BUY', type='MARKET', quantity=(float(positioned_amount) * leverage))
                positions[ticker] = 'Buy'
                # comment above out, to only entry long / short. Keep active, to enter short & long.
                pickle.dump(positions, pos)

        return client.futures_create_order(symbol=(ticker+'USDT'), side='BUY', type='MARKET', quantity=(float(amount) * leverage))

    elif str(data) == 'sell':
        #LOG
        with open('tradelog.txt', 'r') as tradelog:
            trade_log = tradelog.read()
        with open('tradelog.txt', 'w') as tradelog:
            trade_log += '[TRADE]: ' + timestamp + ' | '  + 'Sym: ' + ticker + ' Sg: ' + strategy + ' Side: ' + 'SELL' + '\n'
            tradelog.write(trade_log)


        if position == 'Buy':
            with open('positions.dat', 'wb') as pos:
                with open('history.dat', 'rb') as history:
                    positioned_amount = pickle.load(history)[ticker]
                    client.futures_create_order(symbol=(ticker+'USDT'), side='SELL', type='MARKET', quantity=(positioned_amount * leverage))

        with open('positions.dat', 'wb') as pos:
            positions[ticker] = 'Sell'
            pickle.dump(positions, pos)
        #positions[ticker] = 'None'
                # Close old position and open new Long position,
        #positions[ticker] = 'Sell'
        # comment above out, to only entry long / short. Keep active, to enter short & long.
        #pickle.dump(positions, pos)

        return client.futures_create_order(symbol=(ticker+'USDT'), side='SELL', type='MARKET', quantity=(float(amount) * leverage))
    else:
        print('Warning: ' + str(data))
        return 'Invalid request data.'

def OpenOrders():
    orders = client.futures_get_open_orders()
    return orders

#print(OpenOrders())
#CreateOrder()
#print(Price())
app.run(host='217.160.63.112', port=80)
