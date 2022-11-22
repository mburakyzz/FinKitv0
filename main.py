import time
from kivy.app import App
import pandas as pd
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager,Screen
from kivy.uix.slider import Slider
from kivy.uix.button import ButtonBehavior,Button
from kivy.uix.image import Image
from kivy.uix.label import Label
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
import page_manager
Config.set('graphics', 'width', '926')
Config.set('graphics', 'height', '428')

class MainApp(App):
    def build(self):
        return Page()

class Page(BoxLayout):
    def __init__(self):
        super().__init__()
    def MainPage(self):
        page_manager.MainPage(self=self)
    def WealthPage(self):
        page_manager.WealthPage(self=self,state='pie',msg='')
MainApp().run()