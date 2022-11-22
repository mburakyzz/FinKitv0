import pyrebase
import requests
import json
from more_itertools import sliced
import numpy as np
import pandas as pd

config = {"apiKey": "AIzaSyDpluZlagKKYJeDIi6kujSjwxlNCPg2Eo4",
          "authDomain": "vedge-the-game.firebaseapp.com",
          "databaseURL": "https://vedge-the-game-default-rtdb.europe-west1.firebasedatabase.app/",
          "projectId": "vedge-the-game",
          "storageBucket": "vedge-the-game.appspot.com",
          "messagingSenderId": "483246013458",
          "appId": "1:483246013458:web:249e18dde2109e2321accb",
          "measurementId": "G-1WVNF3RKXQ"}

firebase = pyrebase.initialize_app(config)
db = firebase.database()

def GetMarket(route):
    result = db.child("markets").child(route).get()
    items =list(result.val().items())
    market_data = []
    for i in range(len(items)):
        market_data.append(items[i][0])
    return market_data

def GetExp(ticker,route):
    result = db.child("markets").child(route).child(ticker).get()
    return result.val()

def GetRealEstatePrice(ticker,exp):
    explanation = exp.split('/')[1]
    tick = str(list(sliced(ticker, 3))[1]).split('1')[0]
    result = db.child("realEstatePrices").child(explanation).child(str(tick)+'+1').get()
    item =list(result.val().items())[-1][1]
    return item

def GetRealEstatePrices(ticker,exp,period):
    explanation = exp.split('/')[1]
    tick = str(list(sliced(ticker, 3))[1]).split('1')[0]
    result = db.child("realEstatePrices").child(explanation).child(str(tick)+'+1').get()
    items = list(result.val().items())
    prices = []
    t = int(items[-1][0])
    period_mult = int(str(period).split('d')[0])
    for i in range(period_mult):
        for j in items:
            if int(j[0]) == int(t-(i*60*60*24)):
                prices.append(int(j[1]))
    price = list(reversed(prices))
    return price

def GetFiatBasketHoldings(ticker):
    result = db.child("fiatBasketHoldings").child(ticker).get()
    items = list(result.val().items())
    data = {}
    for i in range(len(items)):
        data.update({items[i][0]:items[i][1]})
    data = sorted(data.items(), key=lambda x: x[1],reverse=True)
    return data

def GetCryptoBasketHoldings(ticker):
    result = db.child("cryptoBasketHoldings").child(ticker).child('holdings').get()
    items = list(result.val().items())
    data = {}
    for i in range(len(items)):
        data.update({items[i][0]:items[i][1]})
    data = sorted(data.items(), key=lambda x: x[1],reverse=True)
    return data

def GetCryptoBasketPrices(ticker,period):
    result = db.child("cryptoBasketHoldings").child(ticker).child('price').get()
    items = list(result.val().items())
    prices = []
    t = int(items[-1][0])
    period_mult = int(str(period).split('d')[0])
    for i in range(period_mult):
        for j in items:
            if int(j[0]) == int(t - (i * 60 * 60 * 24)):
                prices.append(int(j[1]))
    price = list(reversed(prices))
    return price

def GetCryptoPrices(ticker,due,type):
    url = 'https://eapi.binance.com/eapi/v1/mark'
    result = list(requests.get(url).json())
    day = due.split('-')[2]
    month = due.split('-')[1].split('-')[0]
    year = due[2:4]
    prices = []
    for i in result:
        if str(i['symbol']).split('-')[0] == ticker:
            if str(i['symbol']).split('-')[1].split('-')[0] == str(year+month+day):
                if str(i['symbol'])[-1] ==type:
                    prices.append([float(str(i['symbol']).split('-')[2].split('-')[0]),float(i['markPrice'])])
    prices.sort()
    return prices
#GetCryptoPrices('ETH','2022-11-18','C')