from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.properties import BooleanProperty, ListProperty
from os.path import dirname, join

class Data_Showcase(Screen):
    fullscreen = BooleanProperty(False)

    def add_widget(self, *args):
        if 'content' in self.ids:
            return self.aids.content.add_widget(*args)
        return super(Data_Showcase, self).add_widget(*args)

class Trident_LayoutApp(App):
    screen_names = ListProperty([])
    hierarchy = ListProperty([])

    def build(self):
        self.buildtitle = "Hello World"
        self.screen = {}
        self.available_screens = ['Data View']
        self.screen_names = self.available_screens
        curdir = dirname(__file__)
        self.available_screens = [join(curdir,'{}.kv'.format(fn)) for fn in self.available_screens]

    def go_previous_screen(self):
        self.index = (self.index - 1) % len(self.available_screens)
        screen = self.load_screen(self.index)

Trident_LayoutApp().run()