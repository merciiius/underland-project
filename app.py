import json
from flask import Flask, request
from binance.client import Client
from binance.enums import *
import os

app = Flask(__name__)

API_KEY = str(os.environ['API_KEY'])
API_SECRET = str(os.environ['API_SECRET'])
TEST_NET = bool(str(os.environ['TEST_NET']))

client = Client(API_KEY,API_SECRET,testnet=TEST_NET)

print(API_KEY)
print(API_SECRET)

@app.route("/")
def hello_world():
    return "Hello Welcome!"

@app.route("/webhook", methods=['POST'])
def webhook():
    data = json.loads(request.data)

    action = data['action']
    symbol = data['ticker']
    usdt = data['quantity(USDT)']
    lev = data['leverage']

    bid = 0
    ask = 0
    usdt = float(usdt)
    lev = int(lev)

    bid = float(client.futures_orderbook_ticker(symbol =symbol)['bidPrice'])
    ask = float(client.futures_orderbook_ticker(symbol =symbol)['askPrice'])

    posiAmt = float(client.futures_position_information(symbol=symbol)[0]['positionAmt'])
    
    if action == "BUY":
        qty_precision = 0
        for j in client.futures_exchange_info()['symbols']:
            if j['symbol'] == symbol:
                qty_precision = int(j['quantityPrecision'])
        Qty_buy = usdt/bid
        Qty_buy = round(Qty_buy,qty_precision)
        print('qty buy : ',Qty_buy)
        client.futures_change_leverage(symbol=symbol,leverage=lev)
        print('leverage : ',lev)
        order_BUY = client.futures_create_order(symbol=symbol, side='BUY', type='MARKET', quantity=Qty_buy)
        print(symbol,": BUY")

    if action == "SELL":
        qty_precision = 0
        for j in client.futures_exchange_info()['symbols']:
            if j['symbol'] == symbol:
                qty_precision = int(j['quantityPrecision'])
        Qty_sell = usdt/ask
        Qty_sell = round(Qty_sell,qty_precision)
        print('qty sell : ',Qty_sell)
        client.futures_change_leverage(symbol=symbol,leverage=lev)
        print('leverage : ',lev)
        order_SELL = client.futures_create_order(symbol=symbol, side='SELL', type='MARKET', quantity=Qty_sell)
        print(symbol,": SELL")
    
    if action == "SL":
        if posiAmt > 0.0 :
            qty_close = float(client.futures_position_information(symbol=symbol)[0]['positionAmt'])
            close_BUY = client.futures_create_order(symbol=symbol, side='SELL', type='MARKET', quantity=qty_close)
            print(symbol,": StopLoss")

        if posiAmt < 0.0 :
            qty_close = float(client.futures_position_information(symbol=symbol)[0]['positionAmt'])
            close_SELL = client.futures_create_order(symbol=symbol, side='BUY', type='MARKET', quantity=qty_close*-1)
            print(symbol,": StopLoss")
    
    if action == "TP":
        if posiAmt > 0.0 :
            qty_close = float(client.futures_position_information(symbol=symbol)[0]['positionAmt'])
            close_BUY = client.futures_create_order(symbol=symbol, side='SELL', type='MARKET', quantity=qty_close)
            print(symbol,": TakeProfit")

        if posiAmt < 0.0 :
            qty_close = float(client.futures_position_information(symbol=symbol)[0]['positionAmt'])
            close_SELL = client.futures_create_order(symbol=symbol, side='BUY', type='MARKET', quantity=qty_close*-1)
            print(symbol,": TakeProfit")

    if action == "CloseBuy":
        qty_close = float(client.futures_position_information(symbol=symbol)[0]['positionAmt'])
        close_BUY = client.futures_create_order(symbol=symbol, side='SELL', type='MARKET', quantity=qty_close)
        print(symbol,": Close Buy")
    
    if action == "CloseSell":
        qty_close = float(client.futures_position_information(symbol=symbol)[0]['positionAmt'])
        close_SELL = client.futures_create_order(symbol=symbol, side='BUY', type='MARKET', quantity=qty_close*-1)
        print(symbol,": Close Sell")

    if action == "test":
        print("TEST!")
    
    print("---------------------------------")

    return {
        "code" : "success",
        "message" : data
    }

if __name__ == '__main__':
    app.run(debug=True)