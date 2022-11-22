import time
from kivy.app import App
import pandas as pd
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager,Screen
from kivy.uix.slider import Slider
from kivy.uix.button import ButtonBehavior,Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.uix.switch import Switch
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, Ellipse, Rectangle, RoundedRectangle
from kivy.config import Config
from kivy.properties import NumericProperty
from kivy_garden.graph import Graph, LinePlot
import numpy as np
from functools import partial
from kivy.metrics import dp
import matplotlib.colors
import yfinance as yf
import requests
import json
from bs4 import BeautifulSoup
import database
import datetime

import page_manager


def print_info(yf_tickers):
    if isinstance(yf_tickers, yf.Ticker):
        print(f"\n{'=' * 80}")
        space = ' '
        print(f"{space * 33}{yf_tickers.info['symbol']}\n")
        for key in yf_tickers.info:
            print(f"--> {key:>29} : {yf_tickers.info[key]}")
    elif isinstance(yf_tickers, yf.Tickers):
        for ticker in yf_tickers.tickers:
            print(f"\n{'=' * 80}")
            space = ' '
            print(f"{space * 33}{ticker.info['symbol']}\n")
            for key in ticker.info.keys():
                print(f"--> {key:>29} : {ticker.info[key]}")
def print_table(yf_tickers):
    if isinstance(yf_tickers, yf.Ticker):
        ticker = yf_tickers
        print(f"| {ticker.info.get('symbol', 'NONE'):<5} | {ticker.info.get('sector', 'NONE'):>25} | " + \
              f"{ticker.info.get('currency', 'NONE'):>4} | {ticker.info.get('quoteType', 'NONE'):>6} | " + \
              f"{ticker.info.get('shortName', 'NONE'):<35} |")
    elif isinstance(yf_tickers, yf.Tickers):
        for ticker in yf_tickers.tickers:
            print(f"| {ticker.info.get('symbol', 'NONE'):<5} | {ticker.info.get('sector', 'NONE'):>25} | " + \
                  f"{ticker.info.get('currency', 'NONE'):>4} | {ticker.info.get('quoteType', 'NONE'):>6} | " + \
                  f"{ticker.info.get('shortName', 'NONE'):<35} |")
def GetPrice(ticker,route,exp):
    if route == 'Fiat/Currencies':
        return yf.Ticker(str(ticker)+str('USD=X')).history(period='2d',interval='1d')['Close'][-1]
    elif route == 'Fiat/Stocks':
        if exp == 'US':
            return yf.Ticker(str(ticker)).history(period='2d', interval='1d')['Close'][-1]
        elif exp == 'TR':
            return yf.Ticker(str(ticker) + str('.IS')).history(period='2d', interval='1d')['Close'][-1]*yf.Ticker(str('TRY')+str('USD=X')).history(period='2d',interval='1d')['Close'][-1]
    elif route == 'Fiat/Savings':
        ticker = ticker.split('_')[0]
        return yf.Ticker(str(ticker)+str('USD=X')).history(period='2d',interval='1d')['Close'][-1]
    elif route == 'Fiat/Baskets':
        if exp == 'US':
            return yf.Ticker(str(ticker)).history(period='2d', interval='1d')['Close'][-1]
        elif exp == 'TR':
            return yf.Ticker(str(ticker) + str('.IS')).history(period='2d', interval='1d')['Close'][-1]*yf.Ticker(str('TRY')+str('USD=X')).history(period='2d',interval='1d')['Close'][-1]
    elif route == 'Fiat/Real Estates':
        return database.GetRealEstatePrice(ticker=ticker,exp=exp)
    elif route == 'Crypto/Currencies':
        return yf.Ticker(str(ticker)+str('-USD')).history(period='2d',interval='1d')['Close'][-1]
    elif route == 'Crypto/Baskets':
        return int(list(database.db.child("cryptoBasketHoldings").child(ticker).child('price').get().val().items())[-1][1])
    elif route == 'Crypto/Savings':
        return yf.Ticker(str(ticker)+str('-USD')).history(period='2d',interval='1d')['Close'][-1]
    elif route == 'Edge/Fiat Futures':
        if exp == 'Stocks/US':
            ticker = ticker.split('-')[0]
            return yf.Ticker(str(ticker)).history(period='2d', interval='1d')['Close'][-1]
        elif exp == 'Stocks/TR':
            ticker = ticker.split('-')[0]
            return yf.Ticker(str(ticker) + str('.IS')).history(period='2d', interval='1d')['Close'][-1]*yf.Ticker(str('TRY')+str('USD=X')).history(period='2d',interval='1d')['Close'][-1]
        elif exp == 'Baskets/US':
            ticker = ticker.split('-')[0]
            return yf.Ticker(str(ticker)).history(period='2d', interval='1d')['Close'][-1]
        elif exp == 'Baskets/TR':
            ticker = ticker.split('-')[0]
            return yf.Ticker(str(ticker) + str('.IS')).history(period='2d', interval='1d')['Close'][-1]*yf.Ticker(str('TRY')+str('USD=X')).history(period='2d',interval='1d')['Close'][-1]
        elif exp == 'Currencies':
            ticker = ticker.split('-')[0]
            return yf.Ticker(str(ticker) + str('USD=X')).history(period='2d', interval='1d')['Close'][-1]
    elif route == 'Edge/Fiat Options':
        if exp == 'Stocks/US':
            return 200
        elif exp == 'Stocks/TR':
            return 200   *yf.Ticker(str('TRY')+str('USD=X')).history(period='2d',interval='1d')['Close'][-1]
        elif exp == 'Baskets/US':
            return 200
        elif exp == 'Baskets/TR':
            return 200     *yf.Ticker(str('TRY')+str('USD=X')).history(period='2d',interval='1d')['Close'][-1]
    elif route == 'Edge/Crypto Futures':
        if exp == 'Currencies':
            ticker = ticker.split('-')[0]
            return yf.Ticker(str(ticker) + str('-USD')).history(period='2d', interval='1d')['Close'][-1]
        elif exp == 'Baskets':
            return 200
    elif route == 'Edge/Crypto Options':
        if exp == 'Currencies':
            return 200
        elif exp == 'Baskets':
            return 200
    else:
        return 404
def GetBalance(account,df_balance):
    result = database.db.child("accounts").child(account).child('balance').get()
    balance_data = list(result.val().items())
    for i in range(len(balance_data)):
        row = balance_data[i]
        ticker = row[0]
        amount = row[1]['amount']
        cost = row[1]['cost']
        route = str(row[1]['route']).split('_')[0]
        exp = str(row[1]['route']).split('_')[1]
        try:
            leverage = row[1]['leverage']
        except:
            leverage = 1
        try:
            due = row[1]['due']
        except:
            due = None
        try:
            rate = row[1]['rate']
        except:
            rate = None
        price = GetPrice(ticker=ticker,route=route,exp=exp)
        value = np.where(leverage>0,amount*(cost+((price-cost)*leverage)),amount*(cost+((cost-price)*abs(leverage))))
        value = np.where(value>0,value,0)
        value_0 = abs(amount)*cost
        df_balance.loc[ticker] = [amount, cost,rate, route,exp, leverage,due,price,value_0,value]
def GetHistoricalPrice(ticker,market,period,interval,priceroute):
    if priceroute == 'yh':
        x = yf.Ticker(str(ticker)+str(market)).history(period=period, interval=interval)
        price = np.array(list(x['Close'].values))
        print(price)
        return price
    elif priceroute == 'Real Estate':
        price = np.array(database.GetRealEstatePrices(ticker=ticker,exp=market,period=period))
        print(price)
        return price
    elif priceroute == 'Crypto Baskets':
        price = np.array(database.GetCryptoBasketPrices(ticker=ticker,period=period))
        return price
def GetTickerInfo(ticker,market):
    try:
        info = yf.Ticker(str(ticker)+str(market)).info['longName']
    except:
        info = yf.Ticker(str(ticker) + str(market)).info['shortName']
    return info

def WealthPageRenderPie(self,state,df,msg):
    self.mid_panel.clear_widgets()
    try:
        self.right_panel.clear_widgets()
    except:
        pass
    self.mid_panel.add_widget(Image(source='img/vertical_line.png',
                                    size_hint=(5 / 375, 1),
                                    pos_hint={'right': 1, 'y': 0}))
    panel = RelativeLayout()
    states = ['All','Fiat','Crypto','Edge']
    if state >= len(states) or state <= 0:
        state =0
    if states[int(state)] != 'All':
        dataframe = df[df['route'].str.contains(str(str(states[state])+'/'))]
    else:
        dataframe = df

    scroll_view = ScrollView(size_hint=(157/375,208/387),
                            pos_hint={'x':9.58/375,'top':(387-118.2)/387},
                            do_scroll_y=True)
    scroll_box = BoxLayout(size_hint_y=None,orientation='vertical',height=len(dataframe)*58)
    scroll_view.add_widget(scroll_box)
    panel.add_widget(scroll_view)
    for i in range(len(dataframe)):
        if str(dataframe['route'].iloc[i]).split('/')[0] == 'Edge':
            if dataframe['amount'].iloc[i] >0:
                button = Button(background_normal='img/edge_ticker_bull.png',
                                background_down='img/edge_ticker_bull.png',
                                text=dataframe.index.values[i],
                                font_size=30,
                                font_name=r'Bangers-Regular.ttf',
                                size_hint=(1,52/208))
                scroll_box.add_widget(button)
            else:
                button = Button(background_normal='img/edge_ticker_bear.png',
                                background_down='img/edge_ticker_bear.png',
                                font_size=30,
                                font_name=r'Bangers-Regular.ttf',
                                text=dataframe.index.values[i],
                                size_hint=(1, 52 / 208))
                scroll_box.add_widget(button)
        elif str(dataframe['route'].iloc[i]).split('/')[0] == 'Fiat':
            button = Button(background_normal='img/fiat_ticker.png',
                            background_down='img/fiat_ticker.png',
                            font_size=30,
                            font_name=r'Bangers-Regular.ttf',
                            text=dataframe.index.values[i],
                            size_hint=(1, 52 / 208))
            scroll_box.add_widget(button)
        elif str(dataframe['route'].iloc[i]).split('/')[0] == 'Crypto':
            button = Button(background_normal='img/crypto_ticker.png',
                            background_down='img/crypto_ticker.png',
                            font_size=30,
                            font_name=r'Bangers-Regular.ttf',
                            text=dataframe.index.values[i],
                            size_hint=(1, 52 / 208))
            scroll_box.add_widget(button)
        button.bind(on_press=partial(WealthPageRenderPie2,self,i,dataframe))


    self.header = Button(background_normal='img/header.png',
                         background_down='img/header.png',
                         size_hint=(353/375,50.51/387),
                         pos_hint={'x':9.58/375,'top':(387-52.49)/387},
                         text=states[state],
                         color=matplotlib.colors.to_rgba('#F0C782', 1),
                         font_size=25,
                         font_name=r'Bangers-Regular.ttf')
    panel.add_widget(self.header)
    self.header_left = Button(background_color=[0,0,0,0],
                              size_hint=(45/375,45/387),
                              pos_hint={'x':29.53/375,'top':(387-55.25)/387})
    self.header_left_img = Image(source='img/header_left.png',
                                  size_hint=(45 / 375, 45 / 387),
                                  pos_hint={'x': 29.53 / 375, 'top': (387 - 55.25) / 387})
    self.header_left.bind(on_press=partial(WealthPageRenderPie,self,state-1,df))
    self.header_right = Button(background_color=[0,0,0,0],
                               size_hint=(45/375,45/387),
                               pos_hint={'x':297.64/375,'top':(387-55.25)/387})
    self.header_right_img = Image(source='img/header_right.png',
                                  size_hint=(45 / 375, 45 / 387),
                                  pos_hint={'x': 297.64 / 375, 'top': (387 - 55.25) / 387})
    self.header_right.bind(on_press=partial(WealthPageRenderPie,self,state+1,df))
    panel.add_widget(self.header_right)
    panel.add_widget(self.header_right_img)
    panel.add_widget(self.header_left)
    panel.add_widget(self.header_left_img)
    self.mid_panel.add_widget(panel)
    WealthPageRenderPie2(self=self,state=state,df=dataframe,msg='')
def WealthPageRenderPie2(self,state,df,msg):
    try:
        roi = np.round(((df['value'].iloc[state]/df['value_0'].iloc[state])-1)*100,2)
        if roi >=0:
            roi = str('+' + str(roi) +' %')
            roi_color = matplotlib.colors.to_rgba('#21E59F', 1)
        else:
            roi = str(str(roi) + ' %')
            roi_color = matplotlib.colors.to_rgba('#E52121', 1)
        if df['price'].iloc[state]>=100:
            price = int(df['price'].iloc[state])
            cost = int(df['cost'].iloc[state])
        elif df['price'].iloc[state] >= 10:
            price = np.round(df['price'].iloc[state], 2)
            cost = np.round(df['cost'].iloc[state], 2)
        else:
            price = np.round(df['price'].iloc[state],4)
            cost = np.round(df['cost'].iloc[state],4)
    except:
        roi = '-'
        price = '-'
        cost = '-'
        roi_color = matplotlib.colors.to_rgba('#385F71', 1)
    self.right_panel.clear_widgets()
    self.return_list = RelativeLayout(size_hint=(164/375,204/387),
                                      pos_hint={'x':187/375,'top':(387-124)/387})
    return_box = Image(source='img/wealth_return.png',size_hint=(1,75/204),
                       pos_hint={'x':0,'top':1})
    return_header = Label(text='Return',size_hint=(1,20.21/204),
                          pos_hint={'x':0,'top':(204-10.21)/204},
                          font_size=20,
                          font_name=r'Bangers-Regular.ttf',
                          color=matplotlib.colors.to_rgba('#21E59F', 1))
    return_text = Label(text=str(roi),size_hint=(1,20.21/204),
                          pos_hint={'x':0,'top':(204-42.53)/204},
                          font_size=20,
                          font_name=r'Baloo.ttf',
                          color=roi_color)
    cost_box = Image(source='img/wealth_cost_price.png',size_hint=(75/164,75/204),
                       pos_hint={'x':0,'top':(204-89.4)/204})
    cost_header = Label(text='COST', size_hint=(74.88/164, 20.21 / 204),
                          pos_hint={'x': 0, 'top': (204 -98.1) / 204},
                          font_size=16,
                          font_name=r'Bangers-Regular.ttf',
                          color=matplotlib.colors.to_rgba('#385F71', 1))
    cost_text = Label(text=str(cost),size_hint=(74.88/164, 20.21 / 204),
                          pos_hint={'x':0,'top':(204-129.66)/204},
                          font_size=12,
                          font_name=r'Baloo.ttf',
                          color=matplotlib.colors.to_rgba('#385F71', 1))
    price_box = Image(source='img/wealth_cost_price.png',size_hint=(75/164,75/204),
                       pos_hint={'x':89.12/164,'top':(204-89.4)/204})
    price_header = Label(text='price', size_hint=(74.88/164, 20.21 / 204),
                          pos_hint={'x': 89.12/164, 'top': (204 - 98.1) / 204},
                          font_size=16,
                          font_name=r'Bangers-Regular.ttf',
                          color=matplotlib.colors.to_rgba('#385F71', 1))
    price_text = Label(text=str(price),size_hint=(74.88/164, 20.21 / 204),
                          pos_hint={'x':89.12/164,'top':(204-129.66)/204},
                          font_size=12,
                          font_name=r'Baloo.ttf',
                          color=matplotlib.colors.to_rgba('#385F71', 1))
    close_pos_box = Button(background_normal='img/close_position.png',
                           background_down='img/close_position.png',
                           size_hint=(1,27.55/204))
    close_pos_header = Label(text='close position',
                             size_hint=(1,27.55/204),
                             font_size=17,
                             font_name=r'Bangers-Regular.ttf',
                             color=matplotlib.colors.to_rgba('#FFF8DC', 1))
    self.return_list.add_widget(return_box)
    self.return_list.add_widget(return_header)
    self.return_list.add_widget(return_text)
    self.return_list.add_widget(cost_box)
    self.return_list.add_widget(cost_header)
    self.return_list.add_widget(cost_text)
    self.return_list.add_widget(price_box)
    self.return_list.add_widget(price_header)
    self.return_list.add_widget(price_text)
    self.return_list.add_widget(close_pos_box)
    self.return_list.add_widget(close_pos_header)
    self.mid_panel.add_widget(self.return_list)
    WealthPageRenderPie3(self=self,state=state,df=df,msg='')
def WealthPageRenderPie3(self,state,df,msg):
    wealth_percentages = []
    routes = []
    total_value = df['value'].sum()
    values = []
    wealth_pie_layout = RelativeLayout(size_hint=(235/468, 235/387),
                                       pos_hint={'x': 27/468, 'top':(387-105.34)/387})
    wealth_pie_total = RelativeLayout(size_hint=(113/468,235/387),
                                      pos_hint={'x':305/458,'top':(387-104.9)/387})
    wealth_pie_total.add_widget(Image(source='img/wealth_pie_total.png',
                                      size_hint=(32.34/113,1)))
    wealth_pie_total.add_widget(Label(text=str(str(int(total_value))+' $'),
                                      size_hint=(68.71/113,19.46/235),
                                      pos_hint={'x':68.72/113,'center_y':.5},
                                      font_size=18,
                                      font_name=r'Baloo.ttf',
                                      color=matplotlib.colors.to_rgba('#F0C782', 1)))
    wealth_pie_header=RelativeLayout(size_hint=(200/468,28.5/387),
                                     pos_hint={'center_x':.5,'top':(387-52.49)/387})
    wealth_pie_header.add_widget(Image(source='img/header.png'))
    for i in range(len(df)):
        route = str(df['route'][i]).split('/')[0]
        routes.append(route)
        value = df['value'][i]
        value_degree = 360 * value / total_value
        values.append(value)
        wealth_percentages.append(value_degree)
    wealth_pie_graph = Graph(xmin=-1, xmax=1, ymin=-1, ymax=1, x_grid=False, y_grid=False,
                             draw_border=False)
    start_deg = 0
    try:
        wealth_pie_header.add_widget(Label(text=str(df.index.values[state]+' '+str(int(100*df['value'].iloc[state]/total_value))+' %'),
                                           font_name=r'Bangers-Regular.ttf',
                                           font_size=16,
                                           color=matplotlib.colors.to_rgba('#F0C782', 1)))
    except:
        pass
    for i in range(len(wealth_percentages)):
        if routes[i] == 'Fiat':
            color = [.702, .898, .502, (np.where(i == state, 1, .75))]
        elif routes[i] == 'Crypto':
            color = [1, .765, .153, (np.where(i == state, 1, .75))]
        else:
            color = [.69, .506, .929, (np.where(i == state, 1, .75))]
        plot = LinePlot(color=color, line_width=1.25)
        plot.points = [(m * np.cos(np.radians(x)),
                        m * np.sin(np.radians(x)))
                       for x in np.arange(start_deg, start_deg + int(wealth_percentages[i]+1 ),1)
                       for m in np.arange(.5,1,.1)]
        wealth_pie_graph.add_plot(plot)
        start_deg = start_deg + wealth_percentages[i]
        if i == state:
            wealth_pie_layout.add_widget(Label(text=str(str(np.round(values[i],2))+' $'),
                                               size_hint=(114.35/235,22.94/235),
                                               pos_hint={'center_x':.5,'center_y':.5},
                                               font_size=17,
                                               font_name=r'Baloo.ttf',
                                               color=color))
    wealth_pie_layout.add_widget(wealth_pie_graph)
    self.right_panel.add_widget(wealth_pie_layout)
    self.right_panel.add_widget(wealth_pie_total)
    self.right_panel.add_widget(wealth_pie_header)

def HandleReturns(account,timeframe,market):
    markets=['All','Fiat','Crypto','Edge']
    returns=[]
    results = database.db.child('accounts').child(account).child('returns').child(markets[int(market)]).get()
    general = list(results.val().items())
    for i in range(timeframe+1):
        if i == timeframe:
            pass
        else:
            try:
                r = np.round((((general[i][1]+100) / (general[i + 1][1]+100))-1)*100,2)
            except:
                r = 0
            returns.append(r)
    returns = np.flip(returns, 0)
    return returns
def WealthPageRenderLine(self,account,timeframe ,state,msg):
    self.mid_panel.clear_widgets()
    try:
        self.right_panel.clear_widgets()
    except:
        pass
    self.mid_panel.add_widget(Image(source='img/vertical_line.png',
                                    size_hint=(5 / 375, 1),
                                    pos_hint={'right': 1, 'y': 0}))
    panel = RelativeLayout()
    states = ['All','Fiat','Crypto','Edge']
    if state >= len(states) or state <= 0:
        state =0
    returns = HandleReturns(account=account, timeframe=timeframe, market=state)
    self.header = Button(background_normal='img/header.png',
                         background_down='img/header.png',
                         size_hint=(353 / 375, 50.51 / 387),
                         pos_hint={'x': 9.58 / 375, 'top': (387 - 87.26) / 387},
                         text=states[state],
                         color=matplotlib.colors.to_rgba('#F0C782', 1),
                         font_size=25,
                         font_name=r'Bangers-Regular.ttf')
    panel.add_widget(self.header)
    self.header_left = Button(background_color=[0, 0, 0, 0],
                              size_hint=(45 / 375, 45 / 387),
                              pos_hint={'x': 29.53 / 375, 'top': (387 - 90.01) / 387})
    self.header_left_img = Image(source='img/header_left.png',
                                 size_hint=(45 / 375, 45 / 387),
                                 pos_hint={'x': 29.53 / 375, 'top': (387 - 90.01) / 387})
    self.header_left.bind(on_press=partial(WealthPageRenderLine, self, account,timeframe,state - 1))
    self.header_right = Button(background_color=[0, 0, 0, 0],
                               size_hint=(45 / 375, 45 / 387),
                               pos_hint={'x': 297.64 / 375, 'top': (387 - 90.01) / 387})
    self.header_right_img = Image(source='img/header_right.png',
                                  size_hint=(45 / 375, 45 / 387),
                                  pos_hint={'x': 297.64 / 375, 'top': (387 - 90.01) / 387})
    self.header_right.bind(on_press=partial(WealthPageRenderLine, self,account,timeframe, state + 1))
    panel.add_widget(self.header_right)
    panel.add_widget(self.header_right_img)
    panel.add_widget(self.header_left)
    panel.add_widget(self.header_left_img)

    self.returns_min = Image(source='img/wealth_returns.png',
                             size_hint=(109.5/375,75/387),
                             pos_hint={'x':(2.39/375),'top':(387-148.19)/387})
    self.returns_min_header = Label(size_hint=(109.5/375,20.21/387),
                                    pos_hint={'x':(2.39/375),'top':(387-157)/387},
                                    text='Min',
                                    color=matplotlib.colors.to_rgba('#E52121', 1),
                                    font_size=16,
                                    font_name=r'Bangers-Regular.ttf')
    self.returns_min_text = Label(size_hint=(109.5/375,24.21/387),
                                    pos_hint={'x':(2.39/375),'top':(387-190)/387},
                                    text=str(str(np.min(np.round(returns,2)))+' %'),
                                    color=matplotlib.colors.to_rgba('#E52121', 1) if np.min(returns)<0 else matplotlib.colors.to_rgba('#21E59F', 1) ,
                                    font_size=14,
                                    font_name=r'Baloo.ttf')
    self.returns_now = Image(source='img/wealth_returns.png',
                             size_hint=(109.5 / 375, 75 / 387),
                             pos_hint={'x': (124.14 / 375), 'top': (387 - 148.19) / 387})
    self.returns_now_header = Label(size_hint=(109.5/375,20.21/387),
                                    pos_hint={'x':(124.14/375),'top':(387-157)/387},
                                    text='Now',
                                    color=matplotlib.colors.to_rgba('#385F71', 1),
                                    font_size=16,
                                    font_name=r'Bangers-Regular.ttf')
    self.returns_now_text = Label(size_hint=(109.5/375,24.21/387),
                                    pos_hint={'x':(124.14/375),'top':(387-190)/387},
                                    text=str(str(np.round(returns,2)[-1])+' %'),
                                    color=matplotlib.colors.to_rgba('#E52121', 1) if returns[-1]<0 else matplotlib.colors.to_rgba('#21E59F', 1),
                                    font_size=14,
                                    font_name=r'Baloo.ttf')
    self.returns_max = Image(source='img/wealth_returns.png',
                             size_hint=(109.5 / 375, 75 / 387),
                             pos_hint={'x': (245.89 / 375), 'top': (387 - 148.19) / 387})
    self.returns_max_header = Label(size_hint=(109.5/375,20.21/387),
                                    pos_hint={'x':(245.89/375),'top':(387-157)/387},
                                    text='Max',
                                    color=matplotlib.colors.to_rgba('#21E59F', 1),
                                    font_size=16,
                                    font_name=r'Bangers-Regular.ttf')
    self.returns_max_text = Label(size_hint=(109.5/375,24.21/387),
                                    pos_hint={'x':(245.89/375),'top':(387-190)/387},
                                    text=str(str(np.max(np.round(returns,2)))+' %'),
                                    color=matplotlib.colors.to_rgba('#E52121', 1) if np.max(returns)<0 else matplotlib.colors.to_rgba('#21E59F', 1) ,
                                    font_size=14,
                                    font_name=r'Baloo.ttf')
    panel.add_widget(self.returns_min)
    panel.add_widget(self.returns_min_header)
    panel.add_widget(self.returns_min_text)
    panel.add_widget(self.returns_now)
    panel.add_widget(self.returns_now_header)
    panel.add_widget(self.returns_now_text)
    panel.add_widget(self.returns_max)
    panel.add_widget(self.returns_max_header)
    panel.add_widget(self.returns_max_text)
    self.mid_panel.add_widget(panel)

    panel2 = RelativeLayout(size_hint=(354/375,74.76/387),
                            pos_hint={'x':10.5/375,'top':(387-235.06)/387})
    timeframe_upper_line = Image(source='img/horizontal_line.png',
                                 size_hint=(1,5/74.76),
                                 pos_hint={'x':0,'top':1})
    panel2.add_widget(timeframe_upper_line)
    timeframe_lower_line = Image(source='img/horizontal_line.png',
                                 size_hint=(1,5/74.76),
                                 pos_hint={'x':0,'y':0})
    panel2.add_widget(timeframe_lower_line)
    timeframe_scroll = ScrollView(size_hint=(1,52/74.76),
                                  pos_hint={'center_x':.5,'center_y':.5},
                                  do_scroll_x=True)
    times = ['1W','1M','6M','1Y']
    times_int = [7,30,180,365]
    timeframe_box = BoxLayout(size_hint_x=None,orientation='horizontal',width=480)
    timeframe_scroll.add_widget(timeframe_box)
    for i in range(len(times)):
        button = Button(background_normal='img/timebox.png',
                        background_down='img/timebox.png',
                        text=str(times[i]),
                        font_name=r'Bangers-Regular.ttf',
                        color=matplotlib.colors.to_rgba('#385F71', 1))
        button.bind(on_press=partial(WealthPageRenderLine, self,account,times_int[i], state))
        timeframe_box.add_widget(button)
    panel2.add_widget(timeframe_scroll)
    panel.add_widget(panel2)
    panel3 = RelativeLayout(size_hint=(.95,243/387),
                           pos_hint={'center_x':.5,'top':(387-85)/387})
    graph = Graph(xmin=0, xmax=len(returns)-1, ymin=int(np.min(returns))-1, ymax=int(np.max(returns))+1,
                  x_grid=False, y_grid=False, draw_border=False,padding=0)
    plot = LinePlot(color=matplotlib.colors.to_rgba('#F0C782', 1), line_width=1.25)
    x=[]
    y=[]
    for i in range(len(returns)):
        x.append(i)
        y.append(returns[i])
    plot.points = [(x[i],y[i]) for i in range(len(x))]
    graph.add_plot(plot)
    panel3.add_widget(graph)
    self.right_panel.add_widget(panel3)
    range_box = Slider(min=0,max=len(returns)-1,background_width=0,
                       cursor_image='img/line_cursor.png',step=1,
                       cursor_height=panel3.height*2,cursor_width=3,padding=0)
    range_box.bind(value=partial(WealthPageRenderLine2,self,returns))
    panel3.add_widget(range_box)
def WealthPageRenderLine2(self,returns,msg,value):
    try:
        self.right_panel.remove_widget(self.r_text)
        self.right_panel.remove_widget(self.t_text)
        self.right_panel.remove_widget(self.r_header)
        self.right_panel.remove_widget(self.t_header)
        self.right_panel.remove_widget(self.r_image)
        self.right_panel.remove_widget(self.t_image)
    except:
        pass
    t = time.time()-((len(returns)-value)*60*60*24)
    m = str(datetime.datetime.fromtimestamp(t)).split('-')[1]
    d = str(datetime.datetime.fromtimestamp(t)).split('-')[2].split(' ')[0]
    self.r_header = Label(text='Return',font_name=r'Bangers-Regular.ttf',
                          font_size=16,size_hint=(80/468,20/387),
                          pos_hint={'x':154/468,'top':(387-60)/387},
                          color=matplotlib.colors.to_rgba('#F0C782', 1))
    self.r_image = Image(source='img/return_image.png',size_hint=(80/468,20/387),
                         pos_hint={'x':234/468,'top':(387-60)/387})
    self.r_text = Label(text=str(str(returns[int(value)])+'%'),size_hint=(80/468,20/387),
                        font_name=r'Baloo.ttf',font_size=13,
                        pos_hint={'x':234/468,'top':(387-60)/387},
                        color=matplotlib.colors.to_rgba('#385F71', 1))

    self.t_header = Label(text='Date',font_name=r'Bangers-Regular.ttf',
                          font_size=16,size_hint=(80/468,20/387),
                          pos_hint={'x':154/468,'top':(387-328)/387},
                          color=matplotlib.colors.to_rgba('#385F71', 1))
    self.t_image = Image(source='img/date_image.png',size_hint=(80/468,20/387),
                         pos_hint={'x':234/468,'top':(387-328)/387})
    self.t_text = Label(text=str(d+'.'+m),size_hint=(80/468,20/387),
                        font_name=r'Baloo.ttf',font_size=13,
                        pos_hint={'x':234/468,'top':(387-328)/387},
                        color=matplotlib.colors.to_rgba('#F0C782', 1))
    self.right_panel.add_widget(self.r_header)
    self.right_panel.add_widget(self.r_image)
    self.right_panel.add_widget(self.r_text)
    self.right_panel.add_widget(self.t_header)
    self.right_panel.add_widget(self.t_image)
    self.right_panel.add_widget(self.t_text)

def FiatPage(self,state,msg):
    self.ids.screen_bottom.clear_widgets()
    self.market_box = RelativeLayout(size_hint=(470/926,360/387),
                                pos_hint={'x':9/926,'top':(387-13.5)/387})
    market_outer = Image(source='img/fiat_market.png',
                         allow_stretch=True,
                         keep_ratio=False)
    self.market_box.add_widget(market_outer)
    pages = list(page_manager.Pages['Fiat'])
    for i in range(len(pages)):
        icon_alpha = np.where(state==i,1,.5)
        button = Button(size_hint=(90/470,45/360),
                        pos_hint={'x':(10+i*90)/470,'top':(360-39)/360},
                        background_color=[0,0,0,0])
        image = Image(size_hint=(90/470,45/360),
                      pos_hint={'x':(10+i*90)/470,'top':(360-39)/360},
                      source=str('img/fiat_markets.png'),
                      keep_ratio=False,
                      allow_stretch=True)
        image2 = Image(source=str('img/fiat_'+str(pages[i])+'.png'),
                       pos_hint={'x':(37.5+i*90)/470,'top':(360-45)/360},
                       size_hint=(35/470,35/360),
                       color=[1,1,1,icon_alpha])
        button.bind(on_press=partial(FiatPage,self,i))
        self.market_box.add_widget(image)
        self.market_box.add_widget(image2)
        self.market_box.add_widget(button)
        if i ==state:
            header = Label(text=str(pages[i]),
                           font_size=18,
                           font_name=r'Bangers-Regular.ttf',
                           pos_hint={'center_x':.5,'top':(360-10)/360},
                           size_hint=(85/470,20/360),
                           color=matplotlib.colors.to_rgba('#000000', 1))
            self.market_box.add_widget(header)
    FiatPage2(self=self,state=state)
    self.ids.screen_bottom.add_widget(self.market_box)
def FiatPage2(self,state):
    pages = list(page_manager.Pages['Fiat'])
    route = str('Fiat/'+str(pages[state]))
    market = database.GetMarket(route=route)
    scroll_scroll = ScrollView(size_hint=(450/470,114/360),
                                pos_hint={'x':10/470,'top':(360-86)/360},
                                do_scroll_x=True)
    scroll_box = BoxLayout(size_hint_x=None,orientation='horizontal',width=len(market)*90)
    scroll_scroll.add_widget(scroll_box)
    for i in range(len(market)):
        img = Button(background_normal='img/market.png',
                     background_down='img/market.png',
                     text=str(market[i]),
                     font_name=r'Bangers-Regular.ttf',
                     font_size=22)
        img.text_size = (img.width, img.height)
        img.halign = 'center'
        img.valign = 'center'
        img.bind(on_press=partial(FiatPage3,self,market[i],route,'30d'))
        scroll_box.add_widget(img)
    self.market_box.add_widget(scroll_scroll)
def FiatPage3(self,ticker,route,period,msg):
    try:
        self.market_box.remove_widget(self.info_label)
        self.market_box.remove_widget(self.info_box)
    except:
        pass
    if route == 'Fiat/Currencies':
        price = yf.Ticker(str(ticker)+str('USD=X')).history(period=period, interval='1d')['Close'].values
        info = GetTickerInfo(ticker=ticker,market='USD=X')
    elif route == 'Fiat/Stocks':
        market_result = database.db.child('markets').child('Fiat').child('Stocks').child(ticker).get()
        market = str(market_result.val())
        if market =='US':
            price = yf.Ticker(str(ticker)).history(period=period, interval='1d')['Close'].values
            info = GetTickerInfo(ticker=ticker, market='')
        elif market == 'TR':
            price_nom = yf.Ticker(str(ticker) + str('.IS')).history(period=period, interval='1d')['Close'].values
            price_usd = yf.Ticker('TRYUSD=X').history(period=period, interval='1d')['Close'].values
            price = []
            for i in range(len(price_nom)):
                price.append(price_nom[i]*price_usd[i])
            info = GetTickerInfo(ticker=ticker, market='.IS')
    elif route == 'Fiat/Savings':
        price = yf.Ticker(str(ticker)+str('USD=X')).history(period=period, interval='1d')['Close'].values
        info = GetTickerInfo(ticker=ticker,market='USD=X')
        rate_result = database.db.child('fiatSavingRates').child(ticker).get()
        rate = float(list(rate_result.val().items())[0][1])
        self.info_box = RelativeLayout(size_hint = (400/470,75/360),
                                  pos_hint= {'center_x':.5,'top':(360-255)/360})
        info_scroll = ScrollView(size_hint=(125/400,.8),
                                 pos_hint={'x':10/400,'center_y':.5},
                                 do_scroll_y=True)
        times = ['1d','1w','1m','6m','1y']
        days = [1,7,30,180,365]
        info_scroll_box = BoxLayout(size_hint_y=None,orientation='vertical',height=len(times)*52)
        self.info_box.add_widget(info_scroll)
        info_scroll.add_widget(info_scroll_box)
        self.info_rate_box = BoxLayout(size_hint = (225/400,50/75),
                                  pos_hint = {'x':150/400,'center_y':.5})
        self.info_box.add_widget(self.info_rate_box)
        for i in range(len(times)):
            self.rate_text = str('100 ' + str(ticker) + ' in ' + str(times[i]) + ' = ' + str(np.round(100+(rate*days[i]/365),3)) + ' ' + str(ticker))
            self.rate_label = Label(text=self.rate_text,
                                    font_size=16,
                                    font_name = r'Bangers-Regular.ttf',
                                    color = matplotlib.colors.to_rgba('#385F71', 1))
            rate_renderer = lambda x,y: [self.info_rate_box.clear_widgets(), self.info_rate_box.add_widget(x)]
            button = Button(background_normal = 'img/timebox.png',
                            text=times[i],
                            font_name=r'Bangers-Regular.ttf',
                            font_size=16,
                            color=matplotlib.colors.to_rgba('#385F71', 1))
            button.bind(on_press=partial(rate_renderer,self.rate_label))
            info_scroll_box.add_widget(button)
        self.market_box.add_widget(self.info_box)
    elif route == 'Fiat/Baskets':
        price = yf.Ticker(str(ticker)).history(period=period, interval='1d')['Close'].values
        info = GetTickerInfo(ticker=ticker, market='')
        holdings_result = database.db.child('fiatBasketHoldings').child(ticker).get()
        holdings = list(holdings_result.val().items())
        self.info_box = RelativeLayout(size_hint = (400/470,75/360),
                                        pos_hint= {'center_x':.5,'top':(360-255)/360})
        info_scroll = ScrollView(do_scroll_y=True)
        info_box = BoxLayout(size_hint_y=None,orientation='vertical',height=len(holdings)*25)
        for i in range(len(holdings)):
            button = Button(background_normal = 'img/holdings.png',
                            background_down = 'img/holdings.png',
                            size_hint_x=(300/400),
                            pos_hint = {'center_x':.5},
                            text = str(str(holdings[i][0])+' '+str(holdings[i][1])+'%'),
                            color = matplotlib.colors.to_rgba('#385F71', 1),
                            font_size=12,
                            font_name = r'Bangers-Regular.ttf')
            info_box.add_widget(button)
        self.info_box.add_widget(info_scroll)
        info_scroll.add_widget(info_box)
        self.market_box.add_widget(self.info_box)
    elif route == 'Fiat/Real Estates':
        exp_result = database.db.child('markets').child('Fiat').child('Real Estates').child(ticker).get()
        exp = str(exp_result.val())
        price = database.GetRealEstatePrices(ticker=ticker,exp=exp,period=period)
        info = str(exp.split('/')[1] + ' ' + str(ticker).split('1')[0][-1]+'+1')

    self.info_label = Label(text=info, font_size=14, font_name=r'Bangers-Regular.ttf',
                       size_hint=(173 / 470, 35 / 360),
                       color= matplotlib.colors.to_rgba('#385F71', 1),
                       pos_hint={'x': 148.5/470, 'top': (360 - 220) / 360})
    self.market_box.add_widget(self.info_label)

    try:
        self.ids.screen_bottom.remove_widget(self.frame)
    except:
        pass
    self.frame = RelativeLayout(size_hint=(426/926,360/387),
                                pos_hint={'x':489/926,'center_y':.5})
    self.ids.screen_bottom.add_widget(self.frame)
    self.upper_frame = RelativeLayout(size_hint=(1,200/426),
                                      pos_hint={'x':0,'top':1})
    self.frame.add_widget(self.upper_frame)
    self.upper_frame2 = RelativeLayout(size_hint=(346/426,1))
    self.upper_frame.add_widget(self.upper_frame2)
    graph = Graph(xmin=0, xmax=len(price)-1, ymin=int(np.min(price)*1000)-1, ymax=int(np.max(price)*1000)+1,
                  x_grid=False, y_grid=False, draw_border=False,padding=0)
    plot = LinePlot(color=matplotlib.colors.to_rgba('#F0C782', 1), line_width=1.25)
    x=[]
    y=[]
    for i in range(len(price)):
        x.append(i)
        y.append(price[i]*1000)
    plot.points = [(x[i],y[i]) for i in range(len(x))]
    graph.add_plot(plot)
    self.upper_frame2.add_widget(graph)
    self.range_box = Slider(min=0,max=len(price)-1,background_width=0,
                            cursor_image='img/line_cursor.png',step=1,
                            cursor_height=self.upper_frame.height*1.25,cursor_width=3,padding=0)
    self.range_box.bind(value=partial(FiatPage4,self,route,ticker,price))
    self.upper_frame2.add_widget(self.range_box)
    FiatPage4(self,route,ticker,price,'',0)
def FiatPage4(self,route,ticker,price,msg,value):
    try:
        self.times_frame.clear_widgets()
    except:
        pass
    t = time.time()-((len(price)-1-value)*60*60*24)
    m = str(datetime.datetime.fromtimestamp(t)).split('-')[1]
    d = str(datetime.datetime.fromtimestamp(t)).split('-')[2].split(' ')[0]
    try:
        self.upper_frame.remove_widget(self.price_tag)
        self.upper_frame.remove_widget(self.price_background)
        self.upper_frame.remove_widget(self.price_text)
        self.upper_frame.remove_widget(self.date_tag)
        self.upper_frame.remove_widget(self.date_background)
        self.upper_frame.remove_widget(self.date_text)
        self.market_box.remove_widget(self.times_frame)
    except:
        pass
    if price[-1]>1:
        round_digits = 2
    else:
        round_digits = 4
    self.price_tag = Label(text='Price',size_hint=(80/426,25/200),
                           font_name=r'Bangers-Regular.ttf',
                           color=matplotlib.colors.to_rgba('#F0C782', 1),
                           pos_hint={'x':346/426,'top':(200-25)/200})
    self.price_background = Image(source='img/return_image.png',
                                  size_hint =(80/426,25/200),
                                  pos_hint ={'x':346/426,'top':(200-50)/200} )
    self.price_text = Label(text=str(str(np.round(price[int(value)],round_digits))+' $'),
                            font_name=r'Baloo.ttf',
                            font_size=11,
                            size_hint =(80/426,25/200),
                            color=matplotlib.colors.to_rgba('#385F71', 1),
                            pos_hint ={'x':346/426,'top':(200-50)/200})
    self.date_tag = Label(text='Date',size_hint=(80/426,25/200),
                          font_name=r'Bangers-Regular.ttf',
                          color=matplotlib.colors.to_rgba('#385F71', 1),
                          pos_hint={'x':346/426,'top':(200-125)/200})
    self.date_background = Image(source='img/date_image.png',
                                 size_hint =(80/426,25/200),
                                 pos_hint ={'x':346/426,'top':(200-150)/200} )
    self.date_text = Label(text=str(d+'.'+m),
                           size_hint =(80/426,25/200),
                           font_name=r'Baloo.ttf',
                           font_size=12,
                           color=matplotlib.colors.to_rgba('#F0C782', 1),
                           pos_hint ={'x':346/426,'top':(200-150)/200})
    self.upper_frame.add_widget(self.price_tag)
    self.upper_frame.add_widget(self.price_background)
    self.upper_frame.add_widget(self.price_text)
    self.upper_frame.add_widget(self.date_tag)
    self.upper_frame.add_widget(self.date_background)
    self.upper_frame.add_widget(self.date_text)

    min_img = Image(source='img/wealth_returns.png',
                    size_hint=(109.5/426,75/360),
                    pos_hint = {'x':0,'top':(360-200)/360})
    min_header = Label(text='Min',
                       font_size=15,
                       font_name=r'Bangers-Regular.ttf',
                       size_hint= (109.5/426,20/360),
                       pos_hint={'x':0,'top':(360-209)/360},
                       color=matplotlib.colors.to_rgba('#E52121', 1))
    min_text = Label(text=str(str(round(np.min(price),round_digits)) + ' $'),
                     font_size=13,
                     font_name=r'Baloo.ttf',
                     size_hint= (109.5/426,20/360),
                     pos_hint={'x':0,'top':(360-245)/360},
                     color=matplotlib.colors.to_rgba('#385F71', 1))
    now_img = Image(source='img/wealth_returns.png',
                    size_hint=(109.5/426,75/360),
                    pos_hint = {'x':121.75/426,'top':(360-200)/360})
    now_header = Label(text='Now',
                       font_size=15,
                       font_name=r'Bangers-Regular.ttf',
                       size_hint= (109.5/426,20/360),
                       pos_hint={'x':121.75/426,'top':(360-209)/360},
                       color=matplotlib.colors.to_rgba('#385F71', 1))
    now_text = Label(text=str(str(round(price[-1],round_digits)) + ' $'),
                     font_size=13,
                     font_name=r'Baloo.ttf',
                     size_hint= (109.5/426,20/360),
                     pos_hint={'x':121.75/426,'top':(360-245)/360},
                     color=matplotlib.colors.to_rgba('#385F71', 1))
    max_img = Image(source='img/wealth_returns.png',
                    size_hint=(109.5/426,75/360),
                    pos_hint = {'x':243.5/426,'top':(360-200)/360})
    max_header = Label(text='Max',
                       font_size=15,
                       font_name=r'Bangers-Regular.ttf',
                       size_hint= (109.5/426,20/360),
                       pos_hint={'x':243.5/426,'top':(360-209)/360},
                       color=matplotlib.colors.to_rgba('#21E59F', 1))
    max_text = Label(text=str(str(round(np.max(price),round_digits)) + ' $'),
                     font_size=13,
                     font_name=r'Baloo.ttf',
                     size_hint= (109.5/426,20/360),
                     pos_hint={'x':243.5/426,'top':(360-245)/360},
                     color=matplotlib.colors.to_rgba('#385F71', 1))
    self.frame.add_widget(min_img)
    self.frame.add_widget(now_img)
    self.frame.add_widget(max_img)
    self.frame.add_widget(min_header)
    self.frame.add_widget(now_header)
    self.frame.add_widget(max_header)
    self.frame.add_widget(min_text)
    self.frame.add_widget(now_text)
    self.frame.add_widget(max_text)

    self.times_frame = RelativeLayout(size_hint=(353/426,75/360))
    times_upper = Image(source='img/horizontal_line.png',
                        size_hint=(1,5/75),
                        pos_hint={'x':0,'top':1})
    times_lower = Image(source='img/horizontal_line.png',
                        size_hint=(1,5/75),
                        pos_hint={'x':0,'y':0})
    times = ['1w','1m','6m','1y']
    days = [7,30,180,365]
    times_scroll = ScrollView(do_scroll_x=True,size_hint=(1,52/75),
                             pos_hint={'x':0,'center_y':.5})
    times_box = BoxLayout(size_hint_x=None,orientation='horizontal',width=len(times)*120)
    for i in range(len(times)):
        button = Button(background_normal='img/timebox.png',
                        background_down='img/timebox.png',
                        size_hint=(120/353,1),
                        text=str(times[i]),
                        font_size=16,
                        font_name=r'Bangers-Regular.ttf',
                        color=matplotlib.colors.to_rgba('#385F71', 1))
        period = (str(days[i])+'d')
        button.bind(on_press=partial(FiatPage3,self,ticker,route,period))
        times_box.add_widget(button)
    times_scroll.add_widget(times_box)
    self.times_frame.add_widget(times_scroll)
    self.times_frame.add_widget(times_upper)
    self.times_frame.add_widget(times_lower)
    self.frame.add_widget(self.times_frame)

    buy_screen_button = Button(background_color=[0,0,0,0],
                               size_hint=(60/426,60/360),
                               pos_hint={'x':365.25/426,'top':(360-254.2)/360})
    buy_screen_img = Image(source='img/buy_screen.png',
                           size_hint=(60/426,60/360),
                           pos_hint={'x':365.25/426,'top':(360-254.2)/360})
    buy_screen_button.bind(on_press=partial(print,'sa'))
    self.frame.add_widget(buy_screen_button)
    self.frame.add_widget(buy_screen_img)
def CryptoPage(self,state,msg):
    self.ids.screen_bottom.clear_widgets()
    self.market_box = RelativeLayout(size_hint=(470/926,360/387),
                                     pos_hint={'x':9/926,'top':(387-13.5)/387})
    market_outer = Image(source='img/crypto_market.png',
                         allow_stretch=True,
                         keep_ratio=False)
    self.market_box.add_widget(market_outer)
    pages = list(page_manager.Pages['Crypto'])
    for i in range(len(pages)):
        icon_alpha = np.where(state==i,1,.5)
        button = Button(size_hint=(150/470,45/360),
                        pos_hint={'x':(10+i*150)/470,'top':(360-39)/360},
                        background_color=[0,0,0,0])
        image = Image(size_hint=(150/470,45/360),
                      pos_hint={'x':(10+i*150)/470,'top':(360-39)/360},
                      source=str('img/crypto_markets.png'),
                      keep_ratio=False,
                      allow_stretch=True)
        image2 = Image(source=str('img/crypto_'+str(pages[i])+'.png'),
                       pos_hint={'x':(72.5+i*150)/470,'top':(360-45)/360},
                       size_hint=(35/470,35/360),
                       color=[1,1,1,icon_alpha])
        button.bind(on_press=partial(CryptoPage,self,i))
        self.market_box.add_widget(image)
        self.market_box.add_widget(image2)
        self.market_box.add_widget(button)
        if i ==state:
            header = Label(text=str(pages[i]),
                           font_size=18,
                           font_name=r'Bangers-Regular.ttf',
                           pos_hint={'center_x':.5,'top':(360-10)/360},
                           size_hint=(85/470,20/360),
                           color=matplotlib.colors.to_rgba('#000000', 1))
            self.market_box.add_widget(header)
    CryptoPage2(self=self,state=state)
    self.ids.screen_bottom.add_widget(self.market_box)
def CryptoPage2(self,state):
    pages = list(page_manager.Pages['Crypto'])
    route = str('Crypto/'+str(pages[state]))
    market = database.GetMarket(route=route)
    scroll_scroll = ScrollView(size_hint=(450/470,114/360),
                                pos_hint={'x':10/470,'top':(360-86)/360},
                                do_scroll_x=True)
    scroll_box = BoxLayout(size_hint_x=None,orientation='horizontal',width=len(market)*90)
    scroll_scroll.add_widget(scroll_box)
    for i in range(len(market)):
        img = Button(background_normal='img/market.png',
                     background_down='img/market.png',
                     text=str(market[i]),
                     font_name=r'Bangers-Regular.ttf',
                     font_size=15)
        img.text_size = (img.width, img.height)
        img.halign = 'center'
        img.valign = 'center'
        img.bind(on_press=partial(CryptoPage3,self,market[i],route,'30d'))
        scroll_box.add_widget(img)
    self.market_box.add_widget(scroll_scroll)
def CryptoPage3(self,ticker,route,period,msg):
    try:
        self.market_box.remove_widget(self.info_label)
        self.market_box.remove_widget(self.info_box)
    except:
        pass
    if route == 'Crypto/Currencies':
        price = yf.Ticker(str(ticker)+str('-USD')).history(period=period, interval='1d')['Close'].values
        info = GetTickerInfo(ticker=ticker,market='-USD')
    elif route == 'Crypto/Savings':
        price = yf.Ticker(str(ticker)+str('-USD')).history(period=period, interval='1d')['Close'].values
        info = GetTickerInfo(ticker=ticker,market='-USD')
        rate_result = database.db.child('cryptoSavingsRate').child(ticker).get()
        rate = rate_result.val()
        self.info_box = RelativeLayout(size_hint = (400/470,75/360),
                                  pos_hint= {'center_x':.5,'top':(360-255)/360})
        info_scroll = ScrollView(size_hint=(125/400,.8),
                                 pos_hint={'x':10/400,'center_y':.5},
                                 do_scroll_y=True)
        times = ['1d','1w','1m','6m','1y']
        days = [1,7,30,180,365]
        info_scroll_box = BoxLayout(size_hint_y=None,orientation='vertical',height=len(times)*52)
        self.info_box.add_widget(info_scroll)
        info_scroll.add_widget(info_scroll_box)
        self.info_rate_box = BoxLayout(size_hint = (225/400,50/75),
                                       pos_hint = {'x':150/400,'center_y':.5})
        self.info_box.add_widget(self.info_rate_box)
        for i in range(len(times)):
            self.rate_text = str('100 ' + str(ticker) + ' in ' + str(times[i]) + ' = ' + str(np.round(100+(rate*days[i]/365),3)) + ' ' + str(ticker))
            self.rate_label = Label(text=self.rate_text,
                                    font_size=16,
                                    font_name = r'Bangers-Regular.ttf',
                                    color = matplotlib.colors.to_rgba('#385F71', 1))
            rate_renderer = lambda x,y: [self.info_rate_box.clear_widgets(), self.info_rate_box.add_widget(x)]
            button = Button(background_normal = 'img/timebox.png',
                            text=times[i],
                            font_name=r'Bangers-Regular.ttf',
                            font_size=16,
                            color=matplotlib.colors.to_rgba('#385F71', 1))
            button.bind(on_press=partial(rate_renderer,self.rate_label))
            info_scroll_box.add_widget(button)
        self.market_box.add_widget(self.info_box)
    elif route == 'Crypto/Baskets':
        price = database.GetCryptoBasketPrices(ticker,period)
        info = str(ticker + ' basket')
        holdings = database.GetCryptoBasketHoldings(ticker=ticker)
        self.info_box = RelativeLayout(size_hint = (400/470,75/360),
                                        pos_hint= {'center_x':.5,'top':(360-255)/360})
        info_scroll = ScrollView(do_scroll_y=True)
        info_box = BoxLayout(size_hint_y=None,orientation='vertical',height=len(holdings)*25)
        for i in range(len(holdings)):
            button = Button(background_normal = 'img/holdings.png',
                            background_down = 'img/holdings.png',
                            size_hint_x=(300/400),
                            pos_hint = {'center_x':.5},
                            text = str(str(holdings[i][0])+' '+str(holdings[i][1])+'%'),
                            color = matplotlib.colors.to_rgba('#385F71', 1),
                            font_size=12,
                            font_name = r'Bangers-Regular.ttf')
            info_box.add_widget(button)
        self.info_box.add_widget(info_scroll)
        info_scroll.add_widget(info_box)
        self.market_box.add_widget(self.info_box)

    self.info_label = Label(text=info, font_size=14, font_name=r'Bangers-Regular.ttf',
                       size_hint=(173 / 470, 35 / 360),
                       color= matplotlib.colors.to_rgba('#385F71', 1),
                       pos_hint={'x': 148.5/470, 'top': (360 - 220) / 360})
    self.market_box.add_widget(self.info_label)

    try:
        self.ids.screen_bottom.remove_widget(self.frame)
    except:
        pass
    self.frame = RelativeLayout(size_hint=(426/926,360/387),
                                pos_hint={'x':489/926,'center_y':.5})
    self.ids.screen_bottom.add_widget(self.frame)
    self.upper_frame = RelativeLayout(size_hint=(1,200/426),
                                      pos_hint={'x':0,'top':1})
    self.frame.add_widget(self.upper_frame)
    self.upper_frame2 = RelativeLayout(size_hint=(346/426,1))
    self.upper_frame.add_widget(self.upper_frame2)
    graph = Graph(xmin=0, xmax=len(price)-1, ymin=int(np.min(price)*1000)-1, ymax=int(np.max(price)*1000)+1,
                  x_grid=False, y_grid=False, draw_border=False,padding=0)
    plot = LinePlot(color=matplotlib.colors.to_rgba('#F0C782', 1), line_width=1.25)
    x=[]
    y=[]
    for i in range(len(price)):
        x.append(i)
        y.append(price[i]*1000)
    plot.points = [(x[i],y[i]) for i in range(len(x))]
    graph.add_plot(plot)
    self.upper_frame2.add_widget(graph)
    self.range_box = Slider(min=0,max=len(price)-1,background_width=0,
                            cursor_image='img/line_cursor.png',step=1,
                            cursor_height=self.upper_frame.height*1.25,cursor_width=3,padding=0)
    self.range_box.bind(value=partial(CryptoPage4,self,route,ticker,price))
    self.upper_frame2.add_widget(self.range_box)
    CryptoPage4(self,route,ticker,price,'',0)
def CryptoPage4(self,route,ticker,price,msg,value):
    try:
        self.times_frame.clear_widgets()
    except:
        pass
    t = time.time()-((len(price)-1-value)*60*60*24)
    m = str(datetime.datetime.fromtimestamp(t)).split('-')[1]
    d = str(datetime.datetime.fromtimestamp(t)).split('-')[2].split(' ')[0]
    try:
        self.upper_frame.remove_widget(self.price_tag)
        self.upper_frame.remove_widget(self.price_background)
        self.upper_frame.remove_widget(self.price_text)
        self.upper_frame.remove_widget(self.date_tag)
        self.upper_frame.remove_widget(self.date_background)
        self.upper_frame.remove_widget(self.date_text)
        self.market_box.remove_widget(self.times_frame)
    except:
        pass
    if price[-1]>1:
        round_digits = 2
    else:
        round_digits = 4
    self.price_tag = Label(text='Price',size_hint=(80/426,25/200),
                           font_name=r'Bangers-Regular.ttf',
                           color=matplotlib.colors.to_rgba('#F0C782', 1),
                           pos_hint={'x':346/426,'top':(200-25)/200})
    self.price_background = Image(source='img/return_image.png',
                                  size_hint =(80/426,25/200),
                                  pos_hint ={'x':346/426,'top':(200-50)/200} )
    self.price_text = Label(text=str(str(np.round(price[int(value)],round_digits))+' $'),
                            font_name=r'Baloo.ttf',
                            font_size=11,
                            size_hint =(80/426,25/200),
                            color=matplotlib.colors.to_rgba('#385F71', 1),
                            pos_hint ={'x':346/426,'top':(200-50)/200})
    self.date_tag = Label(text='Date',size_hint=(80/426,25/200),
                          font_name=r'Bangers-Regular.ttf',
                          color=matplotlib.colors.to_rgba('#385F71', 1),
                          pos_hint={'x':346/426,'top':(200-125)/200})
    self.date_background = Image(source='img/date_image.png',
                                 size_hint =(80/426,25/200),
                                 pos_hint ={'x':346/426,'top':(200-150)/200} )
    self.date_text = Label(text=str(d+'.'+m),
                           size_hint =(80/426,25/200),
                           font_name=r'Baloo.ttf',
                           font_size=12,
                           color=matplotlib.colors.to_rgba('#F0C782', 1),
                           pos_hint ={'x':346/426,'top':(200-150)/200})
    self.upper_frame.add_widget(self.price_tag)
    self.upper_frame.add_widget(self.price_background)
    self.upper_frame.add_widget(self.price_text)
    self.upper_frame.add_widget(self.date_tag)
    self.upper_frame.add_widget(self.date_background)
    self.upper_frame.add_widget(self.date_text)

    min_img = Image(source='img/wealth_returns.png',
                    size_hint=(109.5/426,75/360),
                    pos_hint = {'x':0,'top':(360-200)/360})
    min_header = Label(text='Min',
                       font_size=15,
                       font_name=r'Bangers-Regular.ttf',
                       size_hint= (109.5/426,20/360),
                       pos_hint={'x':0,'top':(360-209)/360},
                       color=matplotlib.colors.to_rgba('#E52121', 1))
    min_text = Label(text=str(str(round(np.min(price),round_digits)) + ' $'),
                     font_size=13,
                     font_name=r'Baloo.ttf',
                     size_hint= (109.5/426,20/360),
                     pos_hint={'x':0,'top':(360-245)/360},
                     color=matplotlib.colors.to_rgba('#385F71', 1))
    now_img = Image(source='img/wealth_returns.png',
                    size_hint=(109.5/426,75/360),
                    pos_hint = {'x':121.75/426,'top':(360-200)/360})
    now_header = Label(text='Now',
                       font_size=15,
                       font_name=r'Bangers-Regular.ttf',
                       size_hint= (109.5/426,20/360),
                       pos_hint={'x':121.75/426,'top':(360-209)/360},
                       color=matplotlib.colors.to_rgba('#385F71', 1))
    now_text = Label(text=str(str(round(price[-1],round_digits)) + ' $'),
                     font_size=13,
                     font_name=r'Baloo.ttf',
                     size_hint= (109.5/426,20/360),
                     pos_hint={'x':121.75/426,'top':(360-245)/360},
                     color=matplotlib.colors.to_rgba('#385F71', 1))
    max_img = Image(source='img/wealth_returns.png',
                    size_hint=(109.5/426,75/360),
                    pos_hint = {'x':243.5/426,'top':(360-200)/360})
    max_header = Label(text='Max',
                       font_size=15,
                       font_name=r'Bangers-Regular.ttf',
                       size_hint= (109.5/426,20/360),
                       pos_hint={'x':243.5/426,'top':(360-209)/360},
                       color=matplotlib.colors.to_rgba('#21E59F', 1))
    max_text = Label(text=str(str(round(np.max(price),round_digits)) + ' $'),
                     font_size=13,
                     font_name=r'Baloo.ttf',
                     size_hint= (109.5/426,20/360),
                     pos_hint={'x':243.5/426,'top':(360-245)/360},
                     color=matplotlib.colors.to_rgba('#385F71', 1))
    self.frame.add_widget(min_img)
    self.frame.add_widget(now_img)
    self.frame.add_widget(max_img)
    self.frame.add_widget(min_header)
    self.frame.add_widget(now_header)
    self.frame.add_widget(max_header)
    self.frame.add_widget(min_text)
    self.frame.add_widget(now_text)
    self.frame.add_widget(max_text)

    self.times_frame = RelativeLayout(size_hint=(353/426,75/360))
    times_upper = Image(source='img/horizontal_line.png',
                        size_hint=(1,5/75),
                        pos_hint={'x':0,'top':1})
    times_lower = Image(source='img/horizontal_line.png',
                        size_hint=(1,5/75),
                        pos_hint={'x':0,'y':0})
    times = ['1w','1m','6m','1y']
    days = [7,30,180,365]
    times_scroll = ScrollView(do_scroll_x=True,size_hint=(1,52/75),
                             pos_hint={'x':0,'center_y':.5})
    times_box = BoxLayout(size_hint_x=None,orientation='horizontal',width=len(times)*120)
    for i in range(len(times)):
        button = Button(background_normal='img/timebox.png',
                        background_down='img/timebox.png',
                        size_hint=(120/353,1),
                        text=str(times[i]),
                        font_size=16,
                        font_name=r'Bangers-Regular.ttf',
                        color=matplotlib.colors.to_rgba('#385F71', 1))
        period = (str(days[i])+'d')
        button.bind(on_press=partial(CryptoPage3,self,ticker,route,period))
        times_box.add_widget(button)
    times_scroll.add_widget(times_box)
    self.times_frame.add_widget(times_scroll)
    self.times_frame.add_widget(times_upper)
    self.times_frame.add_widget(times_lower)
    self.frame.add_widget(self.times_frame)

    buy_screen_button = Button(background_color=[0,0,0,0],
                               size_hint=(60/426,60/360),
                               pos_hint={'x':365.25/426,'top':(360-254.2)/360})
    buy_screen_img = Image(source='img/buy_screen.png',
                           size_hint=(60/426,60/360),
                           pos_hint={'x':365.25/426,'top':(360-254.2)/360})
    buy_screen_button.bind(on_press=partial(print,'sa'))
    self.frame.add_widget(buy_screen_button)
    self.frame.add_widget(buy_screen_img)

def EdgePage(self,state,msg):
    self.ids.screen_bottom.clear_widgets()
    self.market_box = RelativeLayout(size_hint=(470/926,360/387),
                                     pos_hint={'x':9/926,'top':(387-13.5)/387})
    market_outer = Image(source='img/edge_market.png',
                         allow_stretch=True,
                         keep_ratio=False)
    self.market_box.add_widget(market_outer)
    pages = list(page_manager.Pages['Edge'])

    self.ids.screen_bottom.add_widget(self.market_box)