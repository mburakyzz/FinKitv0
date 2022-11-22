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
import functions

account = 'terrarossa'
Pages = {'Fiat':['Currencies','Stocks','Savings','Baskets','Real Estates'],
         'Crypto':['Currencies','Savings','Baskets'],
         'Edge':['Fiat Futures','Fiat Options','Crypto Futures','Crypto Options']}
df_balance = pd.DataFrame(columns=['amount','cost','rate','route','exp','leverage','due','price','value_0','value'])
functions.GetBalance(account=account, df_balance=df_balance)
df_balance = df_balance.sort_values(by=['value'], ascending=False)

def MainPage(self):
    self.ids.screen_bottom.clear_widgets()
    background = Image(source='img/main.png', allow_stretch=True,keep_ratio=False)

    fiat_button = Button(background_color=[1,1,1,0],
                         size_hint=(66.94/926,66.94/387),
                         pos_hint={'x':138.32/926,'top':(387-19.31)/387})
    fiat_button.bind(on_press=partial(FiatPage,self))
    self.ids.screen_bottom.add_widget(fiat_button)

    crypto_button = Button(background_color=[1,1,1,0],
                             size_hint=(66.94/926,66.94/387),
                             pos_hint={'x':264.57/926,'top':(387-52.77)/387})
    crypto_button.bind(on_press=partial(CryptoPage,self))
    self.ids.screen_bottom.add_widget(crypto_button)

    edge_button = Button(background_color=[1,1,1,0],
                         size_hint=(66.94/926,66.94/387),
                         pos_hint={'x':390.8/926,'top':(387-19.31)/387})
    edge_button.bind(on_press=partial(EdgePage,self))
    self.ids.screen_bottom.add_widget(edge_button)

    vs_button = Button(background_color=[1,1,1,0],
                         size_hint=(66.94/926,66.94/387),
                         pos_hint={'x':459.83/926,'top':(387-300.75)/387})
    vs_button.bind(on_press=partial(VsPage,self))
    self.ids.screen_bottom.add_widget(vs_button)

    strategy_button = Button(background_color=[1,1,1,0],
                         size_hint=(66.94/926,66.94/387),
                         pos_hint={'x':586.07/926,'top':(387-267.28)/387})
    strategy_button.bind(on_press=partial(StrategyPage,self))
    self.ids.screen_bottom.add_widget(strategy_button)

    league_button = Button(background_color=[1,1,1,0],
                         size_hint=(66.94/926,66.94/387),
                         pos_hint={'x':712.3/926,'top':(387-300.75)/387})
    league_button.bind(on_press=partial(LeaguePage,self))
    self.ids.screen_bottom.add_widget(league_button)

    self.ids.screen_bottom.add_widget(background)

def WealthPage(self,state,msg):
    global account
    self.ids.screen_bottom.clear_widgets()
    left_panel = RelativeLayout(size_hint=(83 / 926, 1), pos_hint={'x': 0, 'y': 0})
    self.ids.screen_bottom.add_widget(left_panel)
    self.mid_panel = RelativeLayout(size_hint=(375 / 926, 1), pos_hint={'x': 83/926, 'y': 0})
    self.ids.screen_bottom.add_widget(self.mid_panel)
    self.right_panel = RelativeLayout(size_hint=(468 / 926, 1), pos_hint={'x': 458/926, 'y': 0})
    self.ids.screen_bottom.add_widget(self.right_panel)
    if state == 'pie':
        opacity = [1,.5]
        functions.WealthPageRenderPie(self=self,state=0,df=df_balance,msg='')
        functions.WealthPageRenderPie2(self=self, state=0, df=df_balance, msg='')
    elif state == 'line':
        opacity = [.5, 1]
        functions.WealthPageRenderLine(self=self, account=account,timeframe=7,state=0, msg='')
    pie_button = Button(background_normal='img/wealth_pie_button.png',
                        background_down='img/wealth_pie_button.png',
                        size_hint=(60/83,170/387),
                        background_color=[1,1,1,opacity[0]],
                        pos_hint={'x':11.57/83,'top':(387-22.1)/387})
    pie_button.bind(on_press=partial(WealthPage,self,'pie'))
    line_button = Button(background_normal='img/wealth_line_button.png',
                            background_down='img/wealth_line_button.png',
                            size_hint=(60/83,170/387),
                            background_color=[1,1,1,opacity[1]],
                            pos_hint={'x':11.57/83,'top':(387-192.1)/387})
    line_button.bind(on_press=partial(WealthPage, self, 'line'))
    left_panel.add_widget(pie_button)
    left_panel.add_widget(line_button)
    left_panel.add_widget(Image(source='img/pie.png', size_hint=(50/83,50/387), pos_hint={'x':16.5/83,'top':(387-82.1)/387}))
    left_panel.add_widget(Image(source='img/line.png', size_hint=(50/83,50/387),pos_hint={'x':16.5/83,'top':(387-252.1)/387}))
    left_panel.add_widget(Image(source='img/vertical_line.png',
                                    size_hint=(5/83,1),pos_hint={'right':1,'y':0}))

def FiatPage(self,msg):
    functions.FiatPage(self=self,state=0,msg='')
def CryptoPage(self,msg):
    functions.CryptoPage(self=self,state=0,msg='')

def EdgePage(self,msg):
    functions.EdgePage(self=self,state=0,msg='')

def VsPage(self,msg):
    self.ids.screen_bottom.clear_widgets()
    print('vs page')

def StrategyPage(self,msg):
    self.ids.screen_bottom.clear_widgets()
    print('strategy page')

def LeaguePage(self,msg):
    self.ids.screen_bottom.clear_widgets()
    print('league page')