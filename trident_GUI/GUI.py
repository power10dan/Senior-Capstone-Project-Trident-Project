from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.properties import NumericProperty, BooleanProperty, ListProperty
from os.path import dirname, join

class DataShowcase(Screen):
    fullscreen = BooleanProperty(False)

    def add_widget(self, *args):
        if 'content' in self.ids:
            return self.ids.content.add_widget(*args)
        return super(DataShowcase, self).add_widget(*args)

class TridentLayoutApp(App):
    index = NumericProperty(-1)
    screen_names = ListProperty([])
    hierarchy = ListProperty([])

    def build(self):
        self.buildtitle = "Hello World"
        self.screens = {}
        self.available_screens = ['TextInputs','DataCarousel']
        self.screen_names = self.available_screens
        cur_dir = dirname(__file__)
        self.available_screens = [join(cur_dir, '{}.kv'.format(fn)) for fn in self.available_screens]
        self.go_next_screen()

    def go_previous_screen(self):
        self.index = (self.index - 1) % len(self.available_screens)
        screen = self.load_screen(self.index)
        sm = self.root.ids.sm
        sm.switch_to(screen, direction='left')

    def go_next_screen(self):
        self.index = (self.index +1) % len(self.available_screens)
        screen = self.load_screen(self.index)
        sm = self.root.ids.sm
        sm.switch_to(screen, direction='right')

    def go_screen(self, idx):
        self.index = idx
        self.root.ids.sm.switch_to(self.load_screen(idx), direction='left')

    def go_hierarchy_previous(self):
        ahr = self.hierarchy
        if len(ahr) == 1:
            return
        if ahr:
            ahr.pop()
        if ahr:
            idx = ahr.pop()
            self.go_screen(idx)

    def  load_screen(self, index):
        if index in self.screens:
            return self.screens[index]
        screen = Builder.load_file(self.available_screens[index].lower())
        self.screens[index] = screen
        return screen


TridentLayoutApp().run()
