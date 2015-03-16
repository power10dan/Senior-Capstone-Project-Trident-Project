from kivy.app import App
from kivy.properties import NumericProperty, BooleanProperty, ListProperty, StringProperty, ObjectProperty
from kivy.uix.label import Label
from kivy.adapters.listadapter import ListAdapter
from kivy.uix.listview import ListView
from kivy.uix.dropdown import DropDown
from kivy.uix.widget import Widget
from kivy.uix.button import Button
import logging
import xml.etree.ElementTree as ET
import re


LOG_FILENAME = 'GUI_log.log'
logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG, format='%(asctime)s %(levelname)s: %(message)s')

xmlFilePath = '..//ui.xml'
     
class SettingsMenu(Widget):
    tree = ET.parse(xmlFilePath)

    vertical_tolerance = NumericProperty(float(list(tree.iter('vertical'))[0].text))
    horizontal_tolerance = NumericProperty(float(list(tree.iter('horizontal'))[0].text))
    gps_spacing = NumericProperty(float(list(tree.iter('gps_spacing'))[0].text))
    antennaHeight = NumericProperty(float(list(tree.iter('antennaHeight'))[0].text))
    phaseCenter = NumericProperty(float(list(tree.iter('phaseCenter'))[0].text))
    
    def dropdown(self,loc):
        receiverList = []
        tree = ET.parse(xmlFilePath)
        RSearch = tree.iter('receiver')
        
        for r in RSearch:
            if (list(r)[0].text).upper() == 'T':
                receiverList.append(str(list(r)[4].text))
        drop = DropDown()
        for receiver in receiverList:
            btn = Button(text='%s' % receiver, size_hint_y=None, height=44)
            btn.bind(on_release=lambda btn: drop.select(btn.text))
            drop.add_widget(btn)
        mainButton = Button(text='Hello', size_hint=(None, None))
        self.ids[loc].bind(on_release=drop.open)
        drop.bind(on_select=lambda instance, x: setattr(mainButton, 'text', x))
        
    def submit(self,horizontal,vertical,gps_spacing):
        tree = ET.parse(xmlFilePath)
        horizontal = float(re.sub('[^\.0-9]','',horizontal))
        vertical = float(re.sub('[^\.0-9]','',vertical))
        gps_spacing = float(re.sub('[^\.0-9]','',gps_spacing))
        
        if self.verifyToleranceValues(horizontal,vertical,gps_spacing):
            if vertical != SettingsMenu.vertical_tolerance:
                list(tree.iter('vertical'))[0].text = str(vertical)
            if horizontal != SettingsMenu.horizontal_tolerance:
                list(tree.iter('horizontal'))[0].text = str(horizontal)
            if gps_spacing != SettingsMenu.gps_spacing:
                list(tree.iter('gps_spacing'))[0].text = str(gps_spacing)
            if horizontal != SettingsMenu.horizontal_tolerance or \
               vertical != SettingsMenu.vertical_tolerance or \
               gps_spacing != SettingsMenu.gps_spacing:
                tree.write(xmlFilePath)

    # Checks tolerance inputs to ensure they are within the allowed range
    # Returns 'False' if values are unacceptable, 'True' otherwise, and creates a warning in GUI_log.log
    def verifyToleranceValues(self, horizontalToleranceInput, altitudeToleranceInput, gps_distance):
        # NOTE: units are in meters
        if horizontalToleranceInput < 0 or horizontalToleranceInput > 0.10:
            logging.warn('horizontal tolerance outside of allowed range - input value between 0.0m and 0.10m')
            return False
        elif altitudeToleranceInput < 0 or altitudeToleranceInput > 0.15:
            logging.warn('altitude tolerance outside of allowed range - input value between 0.0m and 0.15m')
            return False
        elif gps_distance != 0.50:
            logging.warn('gps_distance outside of allowed range - only currently accepted value is 0.50m')
            return False
        else:
            return True


class DataOutput(Widget):
    pass
               
class Poseidon(Widget):
    pass
    
class TridentApp(App):
    def build(self):
        gui = Poseidon()
        return gui
                
if __name__ == "__main__":
    TridentApp().run()

