from kivy.uix.boxlayout import BoxLayout
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.properties import NumericProperty, BooleanProperty, ListProperty, StringProperty
from os.path import dirname, join
from kivy.uix.settings import SettingsWithSidebar
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.properties import ObjectProperty, OptionProperty
from kivy.uix.label import Label
from kivy.adapters.simplelistadapter import SimpleListAdapter
from kivy.uix.listview import ListView
import logging
import xml.etree.ElementTree as ET

LOG_FILENAME = 'GUI_log.log'
logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG, format='%(asctime)s %(levelname)s: %(message)s')



xmlFilePath = '..\ui.xml'

class DataShowcase(Screen):
    fullscreen = BooleanProperty(False)
    
    tree = ET.parse(xmlFilePath)
    
    vertical_tolerance = float(list(tree.iter('vertical'))[0].text)
    horizontal_tolerance = float(list(tree.iter('horizontal'))[0].text)
    gps_spacing = float(list(tree.iter('gps_spacing'))[0].text)
    
    def add_widget(self, *args):
        if 'content' in self.ids:
            return self.ids.content.add_widget(*args)
        return super(DataShowcase, self).add_widget(*args)

class TridentLayoutApp(App):
    index = NumericProperty(-1)
    screen_names = ListProperty([])
    hierarchy = ListProperty([])

    
    def build(self):
        
        
        self.buildtitle = "Poseidon Build"
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
        sm.switch_to(screen, direction='right')

    def go_next_screen(self):
        self.index = (self.index +1) % len(self.available_screens)
        screen = self.load_screen(self.index)
        sm = self.root.ids.sm
        sm.switch_to(screen, direction='left')
        
    def popup_open(self):
        list_simple_adapter = SimpleListAdapter(data = ["Router 1", "Router 2", "Router 3"], cls=Label)
        list_view = ListView(adapter = list_simple_adapter)
        popup = Popup(title="Router Selections", content=list_view,size_hint = (None, None), size=(250,250))
        popup.open()
        
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

    def load_screen(self, index):
        if index in self.screens:
            return self.screens[index]
        screen = Builder.load_file(self.available_screens[index].lower())
        self.screens[index] = screen
        return screen
        
    def display_settings(self, settings):
        p = self.settings_popup
        if p is None:
            self.settings_popup = p = Popup(content=settings, title= 'Settings', size_hint=(0.8, 0.8))
        if p.content is not settings:
            p.content = settings
        p.open()

    def set_settings_cls(self, panel_type):
        self.settings_cls = panel_type
        
    def set_display_type(self, display_type):
        self.destroy_settings()
        self.display_type = display_type

    def submit(self):
        tree = ET.parse(xmlFilePath)
        print DataShowcase.vertical_tolerance
        list(tree.iter('vertical'))[0].text = str(DataShowcase.vertical_tolerance)
        list(tree.iter('horizontal'))[0].text = str(DataShowcase.horizontal_tolerance)
        list(tree.iter('gps_spacing'))[0].text = str(DataShowcase.gps_spacing)
        tree.write(xmlFilePath)
        
    # Checks tolerance inputs to ensure they are within the allowed range
    # Returns 'False' if values are unacceptable, 'True' otherwise, and creates a warning in GUI_log.log
    def verifyToleranceValues(self, horizontalToleranceInput, altitudeToleranceInput):
        # NOTE: units are in meters

        if horizontalToleranceInput < 0 or horizontalToleranceInput > 0.10:
            logging.warn('horizontal tolerance outside of allowed range - input value between 0.0m and 0.10m')
            return False
        elif altitudeToleranceInput < 0 or altitudeToleranceInput > 0.15:
            logging.warn('altitude tolerance outside of allowed range - input value between 0.0m and 0.10m')
            return False
        else:
            return True
            
            
TridentLayoutApp().run()

