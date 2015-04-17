from kivy.app import App
from kivy.properties import NumericProperty, BooleanProperty, ListProperty, StringProperty, ObjectProperty
from kivy.uix.label import Label
from kivy.adapters.listadapter import ListAdapter
from kivy.uix.listview import ListView
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
import logging
import xml.etree.ElementTree as ET
import re



LOG_FILENAME = 'GUI_log.log'
logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG, format='%(asctime)s %(levelname)s: %(message)s')

xmlFilePath = './/ui.xml'
     
class SettingsMenu(GridLayout):
    tree = ET.parse(xmlFilePath)

    vertical_tolerance = NumericProperty(float(list(tree.iter('vertical'))[0].text))
    horizontal_tolerance = NumericProperty(float(list(tree.iter('horizontal'))[0].text))
    gps_spacing = NumericProperty(float(list(tree.iter('gps_spacing'))[0].text))
    antennaHeight = NumericProperty(float(list(tree.iter('antennaHeight'))[0].text))
    phaseCenter = NumericProperty(float(list(tree.iter('phaseCenter'))[0].text))
      
    def setReceiver(self, receiver):
        print receiver
        
    def dropdown(self,button,title):
        RSearch = ET.parse(xmlFilePath).iter('receiver')
        layout = BoxLayout(orientation='vertical')
        popup = Popup(attach_to=self,title=str(title),title_align = 'center',size_hint = (.5,.5))
        for r in RSearch:
            if (list(r)[0].text).upper() == 'F':
                btn = Button(text='%s' % str(list(r)[4].text))
                btn.bind(on_press = lambda x: setattr(button, 'text', str(x.text)))
                btn.bind(on_release = popup.dismiss)
                layout.add_widget(btn)
        popup.content = layout
        #popup.bind(on_dismiss = self.setReceiver)
        popup.open()
        
    def submit(self,horizontal,vertical,gps_spacing,antennaHeight,phaseCenter):
        tree = ET.parse(xmlFilePath)
        horizontal = float(re.sub('[^\.0-9]','',horizontal))
        vertical = float(re.sub('[^\.0-9]','',vertical))
        gps_spacing = float(re.sub('[^\.0-9]','',gps_spacing))
        antennaHeight = float(re.sub('[^\.0-9]','',antennaHeight))
        phaseCenter = float(re.sub('[^\.0-9]','',phaseCenter))
        
        updateTolerance = False
        if self.verifyToleranceValues(horizontal,vertical,gps_spacing):
            if vertical != self.vertical_tolerance:
                updateTolerance = True
                list(tree.iter('vertical'))[0].text = str(vertical)
            if horizontal != self.horizontal_tolerance:
                updateTolerance = True
                list(tree.iter('horizontal'))[0].text = str(horizontal)
            if gps_spacing != self.gps_spacing:
                updateTolerance = True
                list(tree.iter('gps_spacing'))[0].text = str(gps_spacing)
            if antennaHeight != self.antennaHeight:
                updateTolerance = True
                list(tree.iter('gps_spacing'))[0].text = str(gps_spacing)
            if phaseCenter != self.phaseCenter:
                updateTolerance = True
                list(tree.iter('gps_spacing'))[0].text = str(gps_spacing)
            if updateTolerance:
                tree.write(xmlFilePath)
                self.vertical_tolerance = vertical
                self.horizontal_tolerance = horizontal
                self.gps_spacing = gps_spacing

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
    def Page(screen):
        DataOutput.navigation.screenName.text = screen

class Poseidon(Widget):
    settings_popup = None
    
    def Settings_Button_pressed(self):
        if self.settings_popup is None:
            self.settings_popup = Popup(attach_to=self, title='Trident Settings', size_hint=(0.7,0.8))
            self.settings_popup.content = SettingsMenu(root = self)
        self.settings_popup.open()
        
    
class TridentApp(App):
    def build(self):
        self.root = Poseidon(app=self)
        
  
if __name__ == "__main__":
    TridentApp().run()

